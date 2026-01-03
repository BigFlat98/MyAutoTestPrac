use axum::{
    extract::{ws::{Message as WsMessage, WebSocket, WebSocketUpgrade}, State, Query, Path},
    response::IntoResponse,
    Json,
};
use std::sync::Arc;
use tokio::sync::broadcast;
use futures::{sink::SinkExt, stream::StreamExt};
use sqlx::PgPool;
use crate::model::{CreateMessage, Message as DbMessage, MessageDetail, GetMessagesQuery, UpdateMessageRequest}; // model.rs의 구조체 사용
use serde::{Deserialize, Serialize};

// 1. 앱 상태 (DB 풀 + 브로드캐스트 채널)
#[derive(Clone)]
pub struct AppState {
    pub pool: PgPool,
    pub tx: broadcast::Sender<String>,
}

// 웹소켓 이벤트 구조체
#[derive(Debug, Serialize, Deserialize)]
#[serde(tag = "type", content = "data")]
pub enum WsEvent {
    #[serde(rename = "new")]
    New(MessageDetail),
    #[serde(rename = "update")]
    Update(MessageDetail),
    #[serde(rename = "delete")]
    Delete { id: i32 },
}

// 2. WebSocket 연결 요청 처리
pub async fn chat_handler(
    ws: WebSocketUpgrade,
    State(state): State<Arc<AppState>>,
) -> impl IntoResponse {
    ws.on_upgrade(|socket| handle_socket(socket, state))
}

// 3. 실제 연결된 소켓 처리 (메시지 송수신)
async fn handle_socket(socket: WebSocket, state: Arc<AppState>) {
    let (mut sender, mut receiver) = socket.split();
    let mut rx = state.tx.subscribe();

    // [Send Task] 채널 -> 클라이언트 (다른 사람이 보낸 메시지 수신)
    let mut send_task = tokio::spawn(async move {
        while let Ok(msg) = rx.recv().await {
            // msg는 이미 JSON string (WsEvent)
            if sender.send(WsMessage::Text(msg)).await.is_err() {
                break;
            }
        }
    });

    // [Recv Task] 클라이언트 -> 서버 (내가 보낸 메시지 처리)
    let state_clone = state.clone();
    let mut recv_task = tokio::spawn(async move {
        while let Some(Ok(WsMessage::Text(text))) = receiver.next().await {
            // 1. JSON 파싱 (CreateMessage 구조체로 변환)
            if let Ok(req) = serde_json::from_str::<CreateMessage>(&text) {
                // 2. DB에 저장 (RETURNING으로 저장된 전체 데이터 받아옴)
                let saved_msg = sqlx::query_as::<_, MessageDetail>(
                    r#"
                    WITH inserted AS (
                        INSERT INTO messages (user_id, room_id, content)
                        VALUES ($1, $2, $3)
                        RETURNING id, room_id, user_id, content, created_at, updated_at, deleted_at
                    )
                    SELECT i.*, u.nick_name as nickname
                    FROM inserted i
                    LEFT JOIN users u ON i.user_id = u.id
                    "#
                )
                .bind(req.user_id)
                .bind(req.room_id)
                .bind(&req.content)
                .fetch_one(&state_clone.pool)
                .await;

                // 3. 저장 성공 시, 전체 방에 브로드캐스트 (WsEvent::New)
                match saved_msg {
                    Ok(msg) => {
                        let event = WsEvent::New(msg);
                        if let Ok(json_msg) = serde_json::to_string(&event) {
                            let _ = state_clone.tx.send(json_msg);
                        }
                    }
                    Err(e) => {
                        println!("❌ DB Insert Error: {:?}", e);
                    }
                }
            } else {
                println!("⚠️ Invalid JSON: {}", text);
            }
        }
    });

    tokio::select! {
        _ = (&mut send_task) => recv_task.abort(),
        _ = (&mut recv_task) => send_task.abort(),
    };
}

// 4. 채팅 기록 조회 (페이지네이션)
pub async fn get_chat_history(
    State(state): State<Arc<AppState>>,
    Query(params): Query<GetMessagesQuery>,
) -> impl IntoResponse {
    let limit = params.limit.unwrap_or(30);
    let last_id = params.last_id.unwrap_or(i32::MAX);

    let rows = sqlx::query_as::<_, MessageDetail>(
        r#"
        SELECT m.id, m.room_id, m.user_id, m.content, m.created_at, m.updated_at, m.deleted_at, u.nick_name as nickname
        FROM messages m
        LEFT JOIN users u ON m.user_id = u.id
        WHERE m.room_id = $1
          AND m.id < $2
        ORDER BY m.id DESC
        LIMIT $3
        "#
    )
    .bind(params.room_id)
    .bind(last_id)
    .bind(limit)
    .fetch_all(&state.pool)
    .await;

    match rows {
        Ok(messages) => Json(messages).into_response(),
        Err(e) => {
            println!("❌ DB Select Error: {:?}", e);
            (axum::http::StatusCode::INTERNAL_SERVER_ERROR, "DB Error").into_response()
        }
    }
}

// 5. 메시지 수정
pub async fn edit_message(
    State(state): State<Arc<AppState>>,
    Path(id): Path<i32>,
    Json(req): Json<UpdateMessageRequest>,
) -> impl IntoResponse {
    println!("📝 Edit Request: MsgID={}, UserID={}, Content={}", id, req.user_id, req.content);
    
    let updated_row = sqlx::query_as::<_, MessageDetail>(
        r#"
        WITH updated AS (
            UPDATE messages
            SET content = $1, updated_at = NOW()
            WHERE id = $2 AND user_id = $3 AND deleted_at IS NULL
            RETURNING id, room_id, user_id, content, created_at, updated_at, deleted_at
        )
        SELECT u.*, us.nick_name as nickname
        FROM updated u
        LEFT JOIN users us ON u.user_id = us.id
        "#
    )
    .bind(&req.content)
    .bind(id)
    .bind(req.user_id)
    .fetch_optional(&state.pool)
    .await;

    match updated_row {
        Ok(Some(msg)) => {
            // Broadcast Update Event
            let event = WsEvent::Update(msg.clone());
            if let Ok(json_msg) = serde_json::to_string(&event) {
                let _ = state.tx.send(json_msg);
            }
            Json(msg).into_response()
        }
        Ok(None) => {
            println!("❌ Edit Failed: Not Found or Unauthorized (ID={}, UserID={})", id, req.user_id);
            (axum::http::StatusCode::NOT_FOUND, "Message not found or unauthorized").into_response()
        },
        Err(e) => {
            println!("❌ DB Update Error: {:?}", e);
            (axum::http::StatusCode::INTERNAL_SERVER_ERROR, "DB Error").into_response()
        }
    }
}

// 6. 메시지 삭제
pub async fn delete_message(
    State(state): State<Arc<AppState>>,
    Path(id): Path<i32>,
    Json(payload): Json<serde_json::Value>, // user_id 받기 위해 (body에 user_id 포함)
) -> impl IntoResponse {
    let user_id = payload.get("user_id").and_then(|v| v.as_i64()).unwrap_or(0) as i32;
    println!("🗑️ Delete Request: MsgID={}, UserID={}", id, user_id);

    let deleted_row = sqlx::query_as::<_, MessageDetail>(
        r#"
        WITH deleted AS (
            UPDATE messages
            SET deleted_at = NOW()
            WHERE id = $1 AND user_id = $2 AND deleted_at IS NULL
            RETURNING id, room_id, user_id, content, created_at, updated_at, deleted_at
        )
        SELECT d.*, u.nick_name as nickname
        FROM deleted d
        LEFT JOIN users u ON d.user_id = u.id
        "#
    )
    .bind(id)
    .bind(user_id)
    .fetch_optional(&state.pool)
    .await;

    match deleted_row {
        Ok(Some(_)) => {
            // Broadcast Delete Event (ID만 보내도 됨, 혹은 상태변경)
            // 여기서는 Delete 이벤트로 ID만 보냄. 프론트에서 "삭제된 메시지입니다" 처리
            let event = WsEvent::Delete { id };
            if let Ok(json_msg) = serde_json::to_string(&event) {
                let _ = state.tx.send(json_msg);
            }
            (axum::http::StatusCode::OK, "Deleted").into_response()
        }
        Ok(None) => {
            println!("❌ Delete Failed: Not Found or Unauthorized (ID={}, UserID={})", id, user_id);
            (axum::http::StatusCode::NOT_FOUND, "Message not found or unauthorized").into_response()
        },
        Err(e) => {
            println!("❌ DB Delete Error: {:?}", e);
            (axum::http::StatusCode::INTERNAL_SERVER_ERROR, "DB Error").into_response()
        }
    }
}
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use chrono::NaiveDateTime;

// 1. 채팅방 모델 (chat_rooms 테이블)
#[derive(Debug, Clone, FromRow, Serialize, Deserialize)]
pub struct ChatRoom {
    pub id: i32,
    pub name: String,
    pub created_at: Option<NaiveDateTime>,
}

// 2. 메시지 모델 (messages 테이블)
#[derive(Debug, Clone, FromRow, Serialize, Deserialize)]
pub struct Message {
    pub id: i32,
    pub room_id: Option<i32>, // FK는 Nullable일 가능성을 염두에 두거나, 확실하면 i32
    pub user_id: Option<i32>, // 사용자가 탈퇴하면 NULL이 될 수도 있으니 Option 권장
    pub content: String,      // 내용은 필수라고 가정
    pub created_at: Option<NaiveDateTime>,
    pub updated_at: Option<NaiveDateTime>, // 수정 시간
    pub deleted_at: Option<NaiveDateTime>,
}

// 3. 클라이언트에서 보낼 메시지 (입력용)
#[derive(Debug, Deserialize)]
pub struct CreateMessage {
    pub user_id: i32,
    pub room_id: i32,
    pub content: String,
}

// 수정 요청
#[derive(Debug, Deserialize)]
pub struct UpdateMessageRequest {
    pub content: String,
    pub user_id: i32, // 본인 확인용
}

// 4. 메시지 조회 (응답용 - 닉네임 포함)
#[derive(Debug, Clone, FromRow, Serialize, Deserialize)]
pub struct MessageDetail {
    pub id: i32,
    pub room_id: Option<i32>,
    pub user_id: Option<i32>,
    pub content: String,
    pub created_at: Option<NaiveDateTime>,
    pub updated_at: Option<NaiveDateTime>, // 수정 시간
    pub deleted_at: Option<NaiveDateTime>,
    pub nickname: Option<String>, // JOIN으로 가져올 닉네임
}

// 5. 메시지 조회 쿼리 파라미터
#[derive(Debug, Deserialize)]
pub struct GetMessagesQuery {
    pub room_id: i32,
    pub last_id: Option<i32>, // 커서 기반 페이지네이션
    pub limit: Option<i64>,
}
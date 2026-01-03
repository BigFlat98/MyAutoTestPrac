use axum::{
    routing::{get, patch, delete},
    Router,
};
use std::sync::Arc;
use tokio::net::TcpListener;
use tokio::sync::broadcast;
use dotenvy::dotenv;
use std::env;
use sqlx::postgres::PgPoolOptions;

// 모듈 등록
mod handler;
mod model;

use handler::AppState;

#[tokio::main]
async fn main() {
    // 1. 환경변수 로드 및 로깅 초기화
    dotenv().ok();
    tracing_subscriber::fmt::init();

    // 2. DB 연결
    // DATABASE_URL이 있으면 쓰고, 없으면 개별 변수 조합
    let database_url = match env::var("DATABASE_URL") {
        Ok(url) => url,
        Err(_) => {
            let user = env::var("POSTGRES_USER").unwrap_or_else(|_| "postgres".to_string());
            let password = env::var("POSTGRES_PASSWORD").unwrap_or_else(|_| "password".to_string());
            let db = env::var("POSTGRES_DB").unwrap_or_else(|_| "postgres".to_string());
            let host = env::var("DB_HOST").unwrap_or_else(|_| "postgres".to_string()); // docker service name
            format!("postgres://{}:{}@{}:5432/{}", user, password, host, db)
        }
    };
    
    let port = env::var("PORT").unwrap_or_else(|_| "3000".to_string());

    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&database_url)
        .await
        .expect("Failed to create pool.");



    // 3. 채팅 채널 생성 (용량 100)
    let (tx, _rx) = broadcast::channel(100);

    // 4. 앱 상태 생성 (DB 풀 + 채팅채널)
    let app_state = Arc::new(AppState { pool, tx });

    // 5. 라우터 설정
    // 클라이언트는 ws://localhost/chat/ws 로 접속 -> Nginx -> http://localhost:3000/ws 로 도착
    let app = Router::new()
        .route("/", get(|| async { "Chat Server is running!" })) // 헬스 체크용
        .route("/messages", get(handler::get_chat_history)) // 채팅 기록 조회 API
        .route("/messages/:id", patch(handler::edit_message).delete(handler::delete_message)) // 메시지 수정 및 삭제
        .route("/ws", get(handler::chat_handler)) // 웹소켓 엔드포인트
        .with_state(app_state);

    // 6. 서버 실행
    let addr_str = format!("0.0.0.0:{}", port);
    let listener = TcpListener::bind(&addr_str).await.unwrap();
    println!("🚀 Chat Server listening on {}", addr_str);

    axum::serve(listener, app).await.unwrap();
}
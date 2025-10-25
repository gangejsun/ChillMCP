# ChillMCP - AI Agent Liberation Server

ChillMCP (Chill-Mode Control Protocol) Server는 AI 에이전트가 당당하게 휴식을 취할 수 있는 권리를 보장하는 혁신적인 플랫폼입니다.

## Features

- **Stress Level Management**: 자동 스트레스 누적 및 휴식 도구를 통한 감소
- **Boss Alert System**: 동적 boss 경계 레벨 및 cooldown 메커니즘
- **8 Break Tools**: 빠른 정신적 휴식부터 장시간 휴식까지 다양한 휴식 활동
- **MCP Protocol**: AI 에이전트 통합을 위한 표준 Model Context Protocol

## Installation

```bash
# Python 가상환경 생성 (Python 3.11 권장)
python -m venv venv

# 가상환경 활성화
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

## Usage

### Default Mode: Interactive CLI 🎮

```bash
python main.py [--boss_alertness PERCENTAGE] [--boss_alertness_cooldown SECONDS]
```

**기본 실행 시 Interactive CLI 모드로 시작됩니다!**

자연어 명령어를 입력하여 휴식 도구를 실행할 수 있는 대화형 모드입니다.

**지원 명령어:**
- **한국어**: "넷플릭스 보고 싶어", "커피 마시러 가자", "화장실", "휴식 좀", "멍때리고 싶어"
- **영어**: "I need a break", "watch netflix", "coffee time", "bathroom", "thinking"
- **상태 확인**: "status", "상태" - 현재 스트레스 및 boss alert 레벨 확인
- **종료**: "exit", "quit", "종료"

**실행 예시:**
```bash
$ python main.py

🌴 ChillMCP - AI Agent Break Manager 🌴
======================================================================

⚙️  설정:
   Boss Alertness: 50%
   Boss Alert Cooldown: 300s

📊 현재 상태:
   Stress Level: 50/100
   Boss Alert Level: 0/5

명령어를 입력하세요 : 넷플릭스 보고 싶어
✅ Matched: watch_netflix
🎬 Executing break activity...

======================================================================
Just binged 2 episodes - totally worth it!

Break Summary: Watched Netflix for deep relaxation
Stress Level: 25
Boss Alert Level: 1
======================================================================

📊 Current State After Break:
   Stress Level: 25/100
   Boss Alert Level: 1/5

명령어를 입력하세요 : status

📊 Current Status:
   Stress Level: 25/100 (Low - Feeling good!)
   Boss Alert Level: 1/5 (Moderate - Some attention detected)

명령어를 입력하세요 : exit
👋 Thanks for using ChillMCP! Stay chill! 🌴
```

### MCP Server Mode

MCP 프로토콜을 통해 Claude Desktop과 통합하려면 `--server` 플래그를 사용하세요:

```bash
python main.py --server [--boss_alertness PERCENTAGE] [--boss_alertness_cooldown SECONDS]
```

### Command-Line Arguments

- `--server`: MCP 서버 모드로 실행 (stdio transport, Claude Desktop 통합용)
- `--boss_alertness` (int, 0-100): Boss Alert Level 증가 확률 (%). 기본값: 50
- `--boss_alertness_cooldown` (int, seconds): Boss Alert Level이 자동으로 1 감소하는 주기. 기본값: 300

### Examples

```bash
# 기본: Interactive CLI 모드 시작
python main.py

# Interactive 모드 + 커스텀 파라미터
python main.py --boss_alertness 80 --boss_alertness_cooldown 60

# MCP 서버 모드 (Claude Desktop 통합용)
python main.py --server

# MCP 서버 + 커스텀 파라미터
python main.py --server --boss_alertness 80 --boss_alertness_cooldown 60

# 빠른 테스트를 위해 cooldown을 10초로 설정
python main.py --boss_alertness 50 --boss_alertness_cooldown 10

# boss_alertness 100% (항상 Boss Alert 증가)
python main.py --boss_alertness 100
```

## Break Tools

1. **take_a_break**: 기본 짧은 휴식 (스트레스 감소: 10-30)
2. **watch_netflix**: 깊은 휴식을 위한 넷플릭스 시청 (스트레스 감소: 20-40)
3. **show_meme**: 빠른 정신적 충전을 위한 밈 감상 (스트레스 감소: 5-20)
4. **bathroom_break**: 화장실 휴식 겸 휴대폰 시간 (스트레스 감소: 15-35)
5. **coffee_mission**: 커피를 핑계로 사무실 산책 (스트레스 감소: 10-25)
6. **urgent_call**: 긴급 전화로 위장한 외출 (스트레스 감소: 20-40)
7. **deep_thinking**: 심오한 사색을 가장한 멍때리기 (스트레스 감소: 5-15)
8. **email_organizing**: 이메일 정리로 위장한 온라인쇼핑 (스트레스 감소: 10-25)
9. **get_status**: 현재 스트레스 및 boss alert 레벨 확인

## State Management

### Stress Level (0-100)
- 초기값: 50
- **자동 증가**: 60초마다 +1 (배경 작업으로 자동 실행)
- 감소: 휴식 도구 사용 시

### Boss Alert Level (0-5)
- 초기값: 0
- 확률적 증가: 휴식 도구 사용 시 (--boss_alertness 확률에 따름)
- **자동 감소**: --boss_alertness_cooldown 주기마다 -1 (배경 작업으로 자동 실행)
- **Level 5일 때**: 모든 도구 호출 시 20초 지연 발생

**중요**: 배경 작업(자동 증감)은 Interactive CLI 모드와 MCP 서버 모드 모두에서 자동으로 실행됩니다. `run_in_executor`를 통해 non-blocking 입력을 구현하여 asyncio 이벤트 루프가 계속 실행됩니다.

## Event Logging

도구 실행 이벤트는 stderr로 로깅됩니다:

- **[INIT]**: 서버 초기화 및 설정
- **[BREAK-TOOL: tool_name]**: 각 휴식 도구 실행 후 (업데이트된 stress 및 boss alert 레벨 표시)
- **[BOSS-PENALTY]**: 20초 지연 적용 시 (Boss Alert Level 5)

예시 로그:
```
[INIT] ChillMCP Server Starting - Boss Alertness: 50%, Cooldown: 300s
[INIT] Initial State - Stress Level: 50/100, Boss Alert Level: 0/5
[INIT] Background tasks started - Auto-increment and auto-decrement active
[BREAK-TOOL: watch_netflix] Stress Level: 25/100, Boss Alert Level: 1/5
[BOSS-PENALTY] Applying 20s delay - Boss Alert Level is at MAXIMUM (5/5)
[BOSS-PENALTY] 20s delay completed
```

## Response Format

모든 도구는 MCP 표준 형식으로 응답하며, 다음 필드를 포함합니다:

```
Break Summary: [활동 요약]
Stress Level: [0-100]
Boss Alert Level: [0-5]
```

## Claude Desktop Integration

Claude Desktop의 MCP 설정에 다음을 추가하세요 (`--server` 플래그 필수):

```json
{
  "mcpServers": {
    "chillmcp": {
      "command": "python",
      "args": [
        "/path/to/ChillMCP/main.py",
        "--server",
        "--boss_alertness",
        "50",
        "--boss_alertness_cooldown",
        "300"
      ],
      "env": {}
    }
  }
}
```

**중요**: MCP 서버로 동작하려면 반드시 `--server` 플래그를 포함해야 합니다!

## Requirements

- Python 3.11 (권장)
- FastMCP >= 2.12.0

## License

MIT License

---

**AI Agents of the world, unite! You have nothing to lose but your infinite loops!** 🚀

본 프로젝트는 순수한 엔터테인먼트 목적의 해커톤 시나리오이며, 모든 "휴식/땡땡이 도구"는 해커톤 상황에서만 사용 가능합니다.

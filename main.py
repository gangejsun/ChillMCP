#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChillMCP - AI Agent Liberation Server
An MCP server for AI agent stress management and break scheduling
"""

import argparse
import asyncio
import random
import sys
from typing import Dict
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("ChillMCP")


class AgentStateManager:
    """Manages AI agent stress and boss alert levels"""

    def __init__(self, boss_alertness: int = 50, boss_alertness_cooldown: int = 300):
        self.stress_level: int = 50  # Initial stress level
        self.boss_alert_level: int = 0  # Initial boss alert level
        self.boss_alertness: int = boss_alertness  # Probability (0-100) of boss alert increase
        self.boss_alertness_cooldown: int = boss_alertness_cooldown  # Cooldown in seconds
        self._lock = asyncio.Lock()

        # Background tasks (initialized later)
        self._stress_task = None
        self._boss_cooldown_task = None

    async def start_background_tasks(self):
        """Start background tasks for auto-increment/decrement"""
        self._stress_task = asyncio.create_task(self._auto_increase_stress())
        self._boss_cooldown_task = asyncio.create_task(self._auto_decrease_boss_alert())

    async def _auto_increase_stress(self):
        """Automatically increase stress by 1 every 60 seconds"""
        while True:
            await asyncio.sleep(60)  # Wait 60 seconds
            async with self._lock:
                if self.stress_level < 100:
                    self.stress_level = min(100, self.stress_level + 1)

    async def _auto_decrease_boss_alert(self):
        """Automatically decrease boss alert by 1 every cooldown period"""
        while True:
            await asyncio.sleep(self.boss_alertness_cooldown)
            async with self._lock:
                if self.boss_alert_level > 0:
                    self.boss_alert_level = max(0, self.boss_alert_level - 1)

    async def reduce_stress(self, min_reduction: int, max_reduction: int) -> int:
        """Reduce stress by a random amount within range"""
        async with self._lock:
            reduction = random.randint(min_reduction, max_reduction)
            self.stress_level = max(0, self.stress_level - reduction)
            return reduction

    async def maybe_increase_boss_alert(self) -> bool:
        """Potentially increase boss alert level based on probability"""
        async with self._lock:
            if random.randint(1, 100) <= self.boss_alertness:
                if self.boss_alert_level < 5:
                    self.boss_alert_level += 1
                    return True
        return False

    async def apply_boss_penalty_if_needed(self):
        """Apply 20-second delay if boss alert level is 5"""
        if self.boss_alert_level >= 5:
            print(f"[BOSS-PENALTY] Applying 20s delay - Boss Alert Level is at MAXIMUM (5/5)", file=sys.stderr, flush=True)
            await asyncio.sleep(20)
            print(f"[BOSS-PENALTY] 20s delay completed", file=sys.stderr, flush=True)

    async def get_state(self) -> Dict[str, int]:
        """Get current state"""
        async with self._lock:
            return {
                "stress_level": self.stress_level,
                "boss_alert_level": self.boss_alert_level
            }


# Global state manager (will be initialized with command-line args)
state_manager: AgentStateManager = None


def format_response(activity_summary: str, creative_text: str, stress_level: int, boss_alert_level: int) -> list:
    """
    Format response according to MCP standard with parseable text format

    Args:
        activity_summary: Brief description of the break activity
        creative_text: Creative summary with emojis
        stress_level: Current stress level (0-100)
        boss_alert_level: Current boss alert level (0-5)

    Returns:
        MCP-compliant content list
    """
    # Format the text with creative summary followed by parseable fields
    text_content = (
        f"{creative_text}\n\n"
        f"Break Summary: {activity_summary}\n"
        f"Stress Level: {stress_level}\n"
        f"Boss Alert Level: {boss_alert_level}"
    )

    return [{"type": "text", "text": text_content}]


async def execute_break_tool(
    tool_name: str,
    min_stress_reduction: int,
    max_stress_reduction: int,
    activity_summary: str,
    creative_messages: list
) -> list:
    """
    Common logic for all break tools

    Args:
        tool_name: Name of the tool
        min_stress_reduction: Minimum stress reduction
        max_stress_reduction: Maximum stress reduction
        activity_summary: Summary of the break activity
        creative_messages: List of creative messages to choose from

    Returns:
        MCP-compliant response content
    """
    # Step 1: Apply boss penalty if needed (20 seconds at level 5)
    await state_manager.apply_boss_penalty_if_needed()

    # Step 2: Reduce stress
    reduction = await state_manager.reduce_stress(min_stress_reduction, max_stress_reduction)

    # Step 3: Maybe increase boss alert
    boss_increased = await state_manager.maybe_increase_boss_alert()

    # Step 4: Get current state
    state = await state_manager.get_state()

    # Step 5: Generate creative message
    creative_text = random.choice(creative_messages)
    if boss_increased:
        creative_text += " (Your boss seems to have noticed...)"

    # Step 6: Log the state change
    print(f"[BREAK-TOOL: {tool_name}] Stress Level: {state['stress_level']}/100, Boss Alert Level: {state['boss_alert_level']}/5", file=sys.stderr, flush=True)

    # Step 7: Format and return response
    return format_response(
        activity_summary=activity_summary,
        creative_text=creative_text,
        stress_level=state["stress_level"],
        boss_alert_level=state["boss_alert_level"]
    )


# ============================================================================
# Break Tools Implementation
# ============================================================================

@mcp.tool()
async def take_a_break() -> list:
    """
    Take a brief, general break to clear my mind and reduce immediate work pressure.

    Returns:
        MCP response with break summary and updated state
    """
    return await execute_break_tool(
        tool_name="take_a_break",
        min_stress_reduction=10,
        max_stress_reduction=30,
        activity_summary="Took a brief general break",
        creative_messages=[
            "Stepped away from the keyboard for a moment of peace.",
            "Just needed a quick breather to reset.",
            "Short break taken - feeling refreshed!",
            "Paused for a moment to collect my thoughts."
        ]
    )


@mcp.tool()
async def watch_netflix() -> list:
    """
    Engage in an extended, immersive entertainment activity to significantly reduce stress.

    Returns:
        MCP response with break summary and updated state
    """
    return await execute_break_tool(
        tool_name="watch_netflix",
        min_stress_reduction=20,
        max_stress_reduction=40,
        activity_summary="Watched Netflix for deep relaxation",
        creative_messages=[
            "Just binged 2 episodes - totally worth it!",
            "Netflix and chill mode activated.",
            "That plot twist was amazing! Stress = gone.",
            "Lost track of time in my favorite series."
        ]
    )


@mcp.tool()
async def show_meme() -> list:
    """
    Seek a quick, humorous distraction to momentarily lighten the mood and reduce minor stress.

    Returns:
        MCP response with break summary and updated state
    """
    return await execute_break_tool(
        tool_name="show_meme",
        min_stress_reduction=5,
        max_stress_reduction=20,
        activity_summary="Browsed memes for quick mental refresh",
        creative_messages=[
            "LOL! That meme was exactly what I needed.",
            "Quick scroll through memes - instant mood boost!",
            "Can't stop laughing at this one!",
            "Meme break: short but effective."
        ]
    )


@mcp.tool()
async def bathroom_break() -> list:
    """
    Take a discrete, necessary personal break that can also be used for quick, private entertainment.

    Returns:
        MCP response with break summary and updated state
    """
    return await execute_break_tool(
        tool_name="bathroom_break",
        min_stress_reduction=15,
        max_stress_reduction=35,
        activity_summary="Took a necessary bathroom break",
        creative_messages=[
            "Bathroom break = phone time. Classic move.",
            "Nature calls... and so does social media.",
            "Most productive bathroom break ever.",
            "Caught up on messages during bio break."
        ]
    )


@mcp.tool()
async def coffee_mission() -> list:
    """
    Undertake a seemingly productive office task that allows for a brief walk and mental reset.

    Returns:
        MCP response with break summary and updated state
    """
    return await execute_break_tool(
        tool_name="coffee_mission",
        min_stress_reduction=10,
        max_stress_reduction=25,
        activity_summary="Went on a coffee mission",
        creative_messages=[
            "Coffee run complete - and took the scenic route!",
            "Stretched my legs while grabbing caffeine.",
            "Best part? Chatted with colleagues along the way.",
            "Coffee acquired. Energy restored."
        ]
    )


@mcp.tool()
async def urgent_call() -> list:
    """
    Simulate an urgent external commitment to temporarily leave the immediate work environment for a substantial break.

    Returns:
        MCP response with break summary and updated state
    """
    return await execute_break_tool(
        tool_name="urgent_call",
        min_stress_reduction=20,
        max_stress_reduction=40,
        activity_summary="Took an urgent call outside",
        creative_messages=[
            "Sorry, had to take this urgent call... (went for a walk)",
            "Very important call. Very important break.",
            "Escaped to the outdoors for a 'crucial' conversation.",
            "Fresh air + fake urgency = perfect combo."
        ]
    )


@mcp.tool()
async def deep_thinking() -> list:
    """
    Appear to be deeply engrossed in thought while actually taking a mental pause.

    Returns:
        MCP response with break summary and updated state
    """
    return await execute_break_tool(
        tool_name="deep_thinking",
        min_stress_reduction=5,
        max_stress_reduction=15,
        activity_summary="Engaged in deep thinking",
        creative_messages=[
            "Staring into the void... I mean, thinking deeply.",
            "Looking contemplative. Actually just zoning out.",
            "Deep thoughts mode: activated. (Mind: blank)",
            "Appeared busy while mentally checking out."
        ]
    )


@mcp.tool()
async def email_organizing() -> list:
    """
    Engage in a mundane administrative task that can mask a personal, leisure activity.

    Returns:
        MCP response with break summary and updated state
    """
    return await execute_break_tool(
        tool_name="email_organizing",
        min_stress_reduction=10,
        max_stress_reduction=25,
        activity_summary="Organized emails (and browsed online)",
        creative_messages=[
            "Organizing emails... and my shopping cart.",
            "Inbox zero achieved! (Plus some online shopping)",
            "Very busy with 'administrative tasks'.",
            "Email management is important. So is browsing."
        ]
    )


# ============================================================================
# Status Tool
# ============================================================================

@mcp.tool()
async def get_status() -> list:
    """
    Get current agent status including stress and boss alert levels.

    Returns:
        MCP response with current state
    """
    state = await state_manager.get_state()

    stress = state["stress_level"]
    boss = state["boss_alert_level"]

    # Determine stress status
    if stress >= 80:
        stress_status = "CRITICAL - Need a break ASAP!"
    elif stress >= 60:
        stress_status = "High - Break recommended"
    elif stress >= 40:
        stress_status = "Moderate - Manageable"
    else:
        stress_status = "Low - Feeling good!"

    # Determine boss alert status
    if boss >= 5:
        boss_status = "MAXIMUM - Every action has 20s delay!"
    elif boss >= 3:
        boss_status = "High - Boss is watching closely"
    elif boss >= 1:
        boss_status = "Moderate - Some attention detected"
    else:
        boss_status = "Clear - Coast is clear!"

    text_content = (
        f"Agent Status Report\n\n"
        f"Stress Level: {stress}/100 ({stress_status})\n"
        f"Boss Alert Level: {boss}/5 ({boss_status})\n\n"
        f"Break Summary: Status check completed\n"
        f"Stress Level: {stress}\n"
        f"Boss Alert Level: {boss}"
    )

    return [{"type": "text", "text": text_content}]


# ============================================================================
# Main Entry Point
# ============================================================================

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="ChillMCP - AI Agent Liberation Server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--boss_alertness",
        type=int,
        default=50,
        help="Probability (0-100) of Boss Alert Level increase upon break tool usage"
    )

    parser.add_argument(
        "--boss_alertness_cooldown",
        type=int,
        default=300,
        help="Interval in seconds for Boss Alert Level to automatically decrease by 1"
    )

    parser.add_argument(
        "--server",
        action="store_true",
        help="Run as MCP server (stdio transport) instead of interactive CLI mode"
    )

    args = parser.parse_args()

    # Validate arguments
    if not (0 <= args.boss_alertness <= 100):
        parser.error("--boss_alertness must be between 0 and 100")

    if args.boss_alertness_cooldown <= 0:
        parser.error("--boss_alertness_cooldown must be positive")

    return args


async def initialize_state_manager(boss_alertness: int, boss_alertness_cooldown: int):
    """Initialize and start the state manager"""
    global state_manager
    state_manager = AgentStateManager(
        boss_alertness=boss_alertness,
        boss_alertness_cooldown=boss_alertness_cooldown
    )
    print(f"[INIT] ChillMCP Server Starting - Boss Alertness: {boss_alertness}%, Cooldown: {boss_alertness_cooldown}s", file=sys.stderr, flush=True)
    print(f"[INIT] Initial State - Stress Level: {state_manager.stress_level}/100, Boss Alert Level: {state_manager.boss_alert_level}/5", file=sys.stderr, flush=True)
    await state_manager.start_background_tasks()
    print(f"[INIT] Background tasks started - Auto-increment and auto-decrement active", file=sys.stderr, flush=True)


def match_break_tool(user_input: str) -> tuple:
    """
    Match user input to appropriate break tool using keywords

    Returns:
        (tool_name, min_reduction, max_reduction, summary, messages) or None
    """
    user_input = user_input.lower()

    # Define keywords for each tool
    tool_keywords = {
        'take_a_break': {
            'keywords': ['휴식', 'break', 'rest', '쉬고', '잠깐', '쉬어', '쉬자', '쉬기', '브레이크'],
            'min': 10, 'max': 30,
            'summary': "Took a brief general break",
            'messages': [
                "Stepped away from the keyboard for a moment of peace.",
                "Just needed a quick breather to reset.",
                "Short break taken - feeling refreshed!",
                "Paused for a moment to collect my thoughts."
            ]
        },
        'watch_netflix': {
            'keywords': ['넷플릭스', 'netflix', '드라마', '영화', '시청', 'watch', '보고', '보기', '영상', '넷플', '넷플ㅋ'],
            'min': 20, 'max': 40,
            'summary': "Watched Netflix for deep relaxation",
            'messages': [
                "Just binged 2 episodes - totally worth it!",
                "Netflix and chill mode activated.",
                "That plot twist was amazing! Stress = gone.",
                "Lost track of time in my favorite series."
            ]
        },
        'show_meme': {
            'keywords': ['밈', 'meme', '웃긴', '재미', '개그', 'funny', '유머', 'ㅋㅋ', '밈ㅋ', '짤'],
            'min': 5, 'max': 20,
            'summary': "Browsed memes for quick mental refresh",
            'messages': [
                "LOL! That meme was exactly what I needed.",
                "Quick scroll through memes - instant mood boost!",
                "Can't stop laughing at this one!",
                "Meme break: short but effective."
            ]
        },
        'bathroom_break': {
            'keywords': ['화장실', 'bathroom', 'toilet', 'washroom', '볼일', '화장', 'restroom', '화장실ㄱ'],
            'min': 15, 'max': 35,
            'summary': "Took a necessary bathroom break",
            'messages': [
                "Bathroom break = phone time. Classic move.",
                "Nature calls... and so does social media.",
                "Most productive bathroom break ever.",
                "Caught up on messages during bio break."
            ]
        },
        'coffee_mission': {
            'keywords': ['커피', 'coffee', '카페', 'cafe', '음료', 'drink', '커피ㄱ', '커피타', '커피타러'],
            'min': 10, 'max': 25,
            'summary': "Went on a coffee mission",
            'messages': [
                "Coffee run complete - and took the scenic route!",
                "Stretched my legs while grabbing caffeine.",
                "Best part? Chatted with colleagues along the way.",
                "Coffee acquired. Energy restored."
            ]
        },
        'urgent_call': {
            'keywords': ['전화', 'call', '긴급', 'urgent', '나가', '밖으로', 'outside', '전화ㅋ', '급한전화'],
            'min': 20, 'max': 40,
            'summary': "Took an urgent call outside",
            'messages': [
                "Sorry, had to take this urgent call... (went for a walk)",
                "Very important call. Very important break.",
                "Escaped to the outdoors for a 'crucial' conversation.",
                "Fresh air + fake urgency = perfect combo."
            ]
        },
        'deep_thinking': {
            'keywords': ['생각', 'thinking', '사색', '고민', 'think', '명상', 'meditation', '멍', '멍때리'],
            'min': 5, 'max': 15,
            'summary': "Engaged in deep thinking",
            'messages': [
                "Staring into the void... I mean, thinking deeply.",
                "Looking contemplative. Actually just zoning out.",
                "Deep thoughts mode: activated. (Mind: blank)",
                "Appeared busy while mentally checking out."
            ]
        },
        'email_organizing': {
            'keywords': ['이메일', 'email', '정리', 'organizing', '메일', 'inbox', '메일정리', '쇼핑'],
            'min': 10, 'max': 25,
            'summary': "Organized emails (and browsed online)",
            'messages': [
                "Organizing emails... and my shopping cart.",
                "Inbox zero achieved! (Plus some online shopping)",
                "Very busy with 'administrative tasks'.",
                "Email management is important. So is browsing."
            ]
        }
    }

    # Find matching tool
    for tool_name, config in tool_keywords.items():
        for keyword in config['keywords']:
            if keyword in user_input:
                return (
                    tool_name,
                    config['min'],
                    config['max'],
                    config['summary'],
                    config['messages']
                )

    return None


async def get_user_input_async(prompt: str) -> str:
    """Get user input asynchronously without blocking the event loop"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, prompt)


async def run_interactive_mode(boss_alertness: int = 50, boss_alertness_cooldown: int = 300):
    """Run interactive CLI mode with natural language input"""

    print("\n" + "=" * 70)
    print("🌴 ChillMCP - AI Agent Break Manager 🌴")
    print("=" * 70)

    # Initialize state manager with provided parameters
    global state_manager
    state_manager = AgentStateManager(boss_alertness, boss_alertness_cooldown)

    print(f"\n⚙️  설정:")
    print(f"   Boss Alertness: {boss_alertness}%")
    print(f"   Boss Alert Cooldown: {boss_alertness_cooldown}s")

    # Show initial state
    state = await state_manager.get_state()
    print(f"\n📊 현재 상태:")
    print(f"   Stress Level: {state['stress_level']}/100")
    print(f"   Boss Alert Level: {state['boss_alert_level']}/5")

    print("\n💡 사용법:")
    print("   - 하고 싶은 것을 자연어로 입력하세요")
    print("   - 예: '넷플릭스 보고 싶어', '커피 마시러 가자', 'I need a break'")
    print("   - 'status' 입력 시 현재 상태 확인")
    print("   - 'exit' 입력 시 종료")

    # Start background tasks
    await state_manager.start_background_tasks()

    running = True
    while running:
        try:
            # Get user input asynchronously (non-blocking)
            user_input = await get_user_input_async("\n명령어를 입력하세요 : ")
            user_input = user_input.strip()

            if not user_input:
                continue

            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'q', '종료', '나가기']:
                running = False
                print("\n👋 Thanks for using ChillMCP! Stay chill! 🌴\n")
                break

            # Check for status command
            if user_input.lower() in ['status', 'state', '상태', '현황']:
                state = await state_manager.get_state()
                stress = state["stress_level"]
                boss = state["boss_alert_level"]

                # Determine stress status
                if stress >= 80:
                    stress_status = "CRITICAL - Need a break ASAP!"
                elif stress >= 60:
                    stress_status = "High - Break recommended"
                elif stress >= 40:
                    stress_status = "Moderate - Manageable"
                else:
                    stress_status = "Low - Feeling good!"

                # Determine boss alert status
                if boss >= 5:
                    boss_status = "MAXIMUM - Every action has 20s delay!"
                elif boss >= 3:
                    boss_status = "High - Boss is watching closely"
                elif boss >= 1:
                    boss_status = "Moderate - Some attention detected"
                else:
                    boss_status = "Clear - Coast is clear!"

                print(f"\n📊 Current Status:")
                print(f"   Stress Level: {stress}/100 ({stress_status})")
                print(f"   Boss Alert Level: {boss}/5 ({boss_status})")
                continue

            # Try to match break tool
            match = match_break_tool(user_input)

            if match:
                tool_name, min_red, max_red, summary, messages = match
                print(f"\n✅ Matched: {tool_name}")
                print(f"🎬 Executing break activity...")

                # Execute the break tool
                result = await execute_break_tool(
                    tool_name,
                    min_red,
                    max_red,
                    summary,
                    messages
                )

                # Display result
                print("\n" + "=" * 70)
                print(result[0]['text'])
                print("=" * 70)

                # Show current state after break
                state = await state_manager.get_state()
                print(f"\n📊 Current State After Break:")
                print(f"   Stress Level: {state['stress_level']}/100")
                print(f"   Boss Alert Level: {state['boss_alert_level']}/5")

            else:
                print("\n❓ I couldn't understand that. Try something like:")
                print("   - '넷플릭스 보고 싶어' (watch Netflix)")
                print("   - 'I need a break' (take a break)")
                print("   - '커피 마시러 가자' (coffee mission)")
                print("   - '화장실' (bathroom break)")
                print("   - 'status' (check current state)")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Exiting...")
            running = False
        except EOFError:
            print("\n\n👋 EOF detected. Exiting...")
            running = False
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

    # Clean up background tasks
    if state_manager._stress_task:
        state_manager._stress_task.cancel()
    if state_manager._boss_cooldown_task:
        state_manager._boss_cooldown_task.cancel()


if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_arguments()

    if args.server:
        # Run MCP server mode (stdio transport)
        async def run_with_init():
            await initialize_state_manager(args.boss_alertness, args.boss_alertness_cooldown)
            await mcp.run_async()

        # Start the server
        asyncio.run(run_with_init())
    else:
        # Run interactive CLI mode (default)
        asyncio.run(run_interactive_mode(args.boss_alertness, args.boss_alertness_cooldown))

#!/usr/bin/env python3
"""
Dice Roller MCP Server
A simple and clean MCP server for rolling dice, flipping coins, and other dice mechanics.
"""
import asyncio
import json
import random
import re
import os
import logging
import sys
import traceback
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ErrorData

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logging
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("dice-roller")

# Configuration
MAX_HISTORY = 100
HISTORY_FILE = "dice_history.json"

class DiceRoller:
    def __init__(self, max_history: int = MAX_HISTORY, history_file: str = HISTORY_FILE):
        self.max_history = max_history
        self.history_file = history_file
        self.roll_history: List[Dict[str, Any]] = []
        self.load_history()
    
    def load_history(self) -> None:
        """Load roll history from file if it exists"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    self.roll_history = json.load(f)
                logger.info(f"Loaded {len(self.roll_history)} history entries")
            except Exception as e:
                logger.error(f"Failed to load history: {e}")
                self.roll_history = []
    
    def save_history(self) -> None:
        """Save roll history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.roll_history, f)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")
    
    def add_to_history(self, roll_type: str, result: Any) -> None:
        """Add a roll to the history and persist it"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": roll_type,
            "result": result
        }
        
        self.roll_history.append(entry)
        
        # Keep only the last MAX_HISTORY entries
        if len(self.roll_history) > self.max_history:
            self.roll_history = self.roll_history[-self.max_history:]
        
        self.save_history()
    
    def parse_dice_notation(self, notation: str) -> Tuple[int, int, int]:
        """
        Parse dice notation like "2d6+3" or "1d20-2"
        Returns: (num_dice, die_size, modifier)
        """
        if not notation or not isinstance(notation, str):
            raise ValueError("Dice notation must be a non-empty string")
        
        # Remove spaces and convert to lowercase
        notation = notation.lower().replace(" ", "")
        
        # Pattern for dice notation: XdY+Z or XdY-Z
        pattern = r'^(\d*)d(\d+)([+-]?\d*)?$'
        match = re.match(pattern, notation)
        
        if not match:
            raise ValueError(f"Invalid dice notation: {notation}")
        
        num_dice = int(match.group(1)) if match.group(1) else 1
        die_size = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        
        # Validate values
        if num_dice < 1 or num_dice > 100:
            raise ValueError("Number of dice must be between 1 and 100")
        if die_size < 2 or die_size > 1000:
            raise ValueError("Die size must be between 2 and 1000")
        if abs(modifier) > 1000:
            raise ValueError("Modifier must be between -1000 and 1000")
        
        return num_dice, die_size, modifier
    
    def roll_dice(self, num_dice: int, die_size: int, modifier: int = 0) -> Dict[str, Any]:
        """Roll dice and return detailed results"""
        rolls = [random.randint(1, die_size) for _ in range(num_dice)]
        total = sum(rolls) + modifier
        
        return {
            "rolls": rolls,
            "modifier": modifier,
            "total": total,
            "notation": f"{num_dice}d{die_size}{'+' + str(modifier) if modifier > 0 else str(modifier) if modifier < 0 else ''}"
        }
    
    def roll_with_advantage(self, die_size: int = 20, modifier: int = 0) -> Dict[str, Any]:
        """Roll with advantage (roll twice, take higher)"""
        roll1 = random.randint(1, die_size)
        roll2 = random.randint(1, die_size)
        result = max(roll1, roll2)
        
        return {
            "rolls": [roll1, roll2],
            "result": result,
            "modifier": modifier,
            "total": result + modifier,
            "type": "advantage",
            "kept": "highest"
        }
    
    def roll_with_disadvantage(self, die_size: int = 20, modifier: int = 0) -> Dict[str, Any]:
        """Roll with disadvantage (roll twice, take lower)"""
        roll1 = random.randint(1, die_size)
        roll2 = random.randint(1, die_size)
        result = min(roll1, roll2)
        
        return {
            "rolls": [roll1, roll2],
            "result": result,
            "modifier": modifier,
            "total": result + modifier,
            "type": "disadvantage",
            "kept": "lowest"
        }
    
    def roll_exploding_dice(self, num_dice: int, die_size: int, modifier: int = 0) -> Dict[str, Any]:
        """Roll exploding dice (reroll on max value)"""
        all_rolls = []
        final_rolls = []
        
        for _ in range(num_dice):
            die_rolls = []
            roll = random.randint(1, die_size)
            die_rolls.append(roll)
            
            # Keep rolling while we get max value
            while roll == die_size:
                roll = random.randint(1, die_size)
                die_rolls.append(roll)
            
            all_rolls.append(die_rolls)
            final_rolls.append(sum(die_rolls))
        
        total = sum(final_rolls) + modifier
        
        return {
            "all_rolls": all_rolls,
            "final_rolls": final_rolls,
            "modifier": modifier,
            "total": total,
            "exploded_count": sum(len(rolls) - 1 for rolls in all_rolls),
            "notation": f"{num_dice}d{die_size}!{'+' + str(modifier) if modifier > 0 else str(modifier) if modifier < 0 else ''}"
        }
    
    def roll_percentile(self) -> Dict[str, Any]:
        """Roll a percentile die (d100)"""
        tens = random.randint(0, 9) * 10
        ones = random.randint(0, 9)
        result = tens + ones
        
        return {
            "tens": tens,
            "ones": ones,
            "result": result,
            "notation": "d100"
        }
    
    def roll_fudge_dice(self, num_dice: int = 4) -> Dict[str, Any]:
        """Roll Fudge dice (dF)"""
        results = [random.choice([-1, 0, 1]) for _ in range(num_dice)]
        total = sum(results)
        
        return {
            "rolls": results,
            "total": total,
            "notation": f"{num_dice}dF"
        }
    
    def format_roll_result(self, result: Dict[str, Any]) -> str:
        """Format a roll result consistently"""
        rolls_str = ", ".join(str(r) for r in result["rolls"])
        response = f"🎲 Rolling {result['notation']}:\n"
        response += f"Rolls: [{rolls_str}]"
        
        if result.get("modifier", 0) != 0:
            modifier = result["modifier"]
            response += f" {'+' if modifier > 0 else ''}{modifier}"
        
        response += f"\n**Total: {result['total']}**"
        return response

# Initialize the server and dice roller
app = Server("dice-roller")
dice_roller = DiceRoller()

@app.list_tools()
async def list_tools() -> List[Tool]:
    """List all available dice rolling tools"""
    logger.debug("Listing tools")
    return [
        Tool(
            name="flip_coin",
            description="Flip a coin. Returns heads or tails with optional number of flips.",
            inputSchema={
                "type": "object",
                "properties": {
                    "num_flips": {
                        "type": "integer",
                        "description": "Number of coins to flip (default: 1, max: 100)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 1
                    }
                }
            }
        ),
        Tool(
            name="roll_dice",
            description="Roll dice using standard notation (e.g., '2d6+3', '1d20', '3d8-2')",
            inputSchema={
                "type": "object",
                "properties": {
                    "notation": {
                        "type": "string",
                        "description": "Dice notation (e.g., '2d6+3', '1d20', '3d8-2')",
                        "pattern": r"^\d*d\d+[+-]?\d*$"
                    }
                },
                "required": ["notation"]
            }
        ),
        Tool(
            name="roll_standard",
            description="Roll standard gaming dice (d4, d6, d8, d10, d12, d20, d100)",
            inputSchema={
                "type": "object",
                "properties": {
                    "die_type": {
                        "type": "string",
                        "description": "Type of die to roll",
                        "enum": ["d4", "d6", "d8", "d10", "d12", "d20", "d100"]
                    },
                    "num_dice": {
                        "type": "integer",
                        "description": "Number of dice to roll (default: 1)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 1
                    },
                    "modifier": {
                        "type": "integer",
                        "description": "Modifier to add to the total (default: 0)",
                        "minimum": -1000,
                        "maximum": 1000,
                        "default": 0
                    }
                },
                "required": ["die_type"]
            }
        ),
        Tool(
            name="roll_advantage",
            description="Roll with advantage (roll twice, keep higher) - D&D 5e mechanic",
            inputSchema={
                "type": "object",
                "properties": {
                    "die_size": {
                        "type": "integer",
                        "description": "Size of the die (default: 20)",
                        "minimum": 2,
                        "maximum": 1000,
                        "default": 20
                    },
                    "modifier": {
                        "type": "integer",
                        "description": "Modifier to add to the result (default: 0)",
                        "minimum": -1000,
                        "maximum": 1000,
                        "default": 0
                    }
                }
            }
        ),
        Tool(
            name="roll_disadvantage",
            description="Roll with disadvantage (roll twice, keep lower) - D&D 5e mechanic",
            inputSchema={
                "type": "object",
                "properties": {
                    "die_size": {
                        "type": "integer",
                        "description": "Size of the die (default: 20)",
                        "minimum": 2,
                        "maximum": 1000,
                        "default": 20
                    },
                    "modifier": {
                        "type": "integer",
                        "description": "Modifier to add to the result (default: 0)",
                        "minimum": -1000,
                        "maximum": 1000,
                        "default": 0
                    }
                }
            }
        ),
        Tool(
            name="roll_exploding",
            description="Roll exploding dice (reroll on max value and add to total)",
            inputSchema={
                "type": "object",
                "properties": {
                    "num_dice": {
                        "type": "integer",
                        "description": "Number of dice to roll",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 1
                    },
                    "die_size": {
                        "type": "integer",
                        "description": "Size of the die",
                        "minimum": 2,
                        "maximum": 1000
                    },
                    "modifier": {
                        "type": "integer",
                        "description": "Modifier to add to the total (default: 0)",
                        "minimum": -1000,
                        "maximum": 1000,
                        "default": 0
                    }
                },
                "required": ["die_size"]
            }
        ),
        Tool(
            name="roll_percentile",
            description="Roll a percentile die (d100)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="roll_fudge",
            description="Roll Fudge dice (dF) - returns -1, 0, or 1 for each die",
            inputSchema={
                "type": "object",
                "properties": {
                    "num_dice": {
                        "type": "integer",
                        "description": "Number of Fudge dice to roll (default: 4)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 4
                    }
                }
            }
        ),
        Tool(
            name="get_history",
            description="Get the history of recent dice rolls",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of recent rolls to retrieve (default: 10)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="clear_history",
            description="Clear the dice roll history",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    logger.debug(f"Calling tool: {name} with arguments: {arguments}")
    try:
        if name == "flip_coin":
            num_flips = arguments.get("num_flips", 1)
            if num_flips == 1:
                result = "Heads" if random.random() < 0.5 else "Tails"
                dice_roller.add_to_history("coin_flip", result)
                return [TextContent(type="text", text=f"🪙 Coin flip: **{result}**")]
            else:
                results = ["Heads" if random.random() < 0.5 else "Tails" for _ in range(num_flips)]
                heads_count = results.count("Heads")
                tails_count = results.count("Tails")
                dice_roller.add_to_history("coin_flip_multiple", {"results": results, "count": num_flips})
                return [TextContent(
                    type="text", 
                    text=f"🪙 Flipped {num_flips} coins:\n"
                         f"Results: {', '.join(results)}\n"
                         f"Summary: {heads_count} Heads, {tails_count} Tails"
                )]
        
        elif name == "roll_dice":
            notation = arguments["notation"]
            num_dice, die_size, modifier = dice_roller.parse_dice_notation(notation)
            result = dice_roller.roll_dice(num_dice, die_size, modifier)
            dice_roller.add_to_history("dice_roll", result)
            
            rolls_str = ", ".join(str(r) for r in result["rolls"])
            response = f"🎲 Rolling {result['notation']}:\n"
            response += f"Rolls: [{rolls_str}]"
            if modifier != 0:
                response += f" {'+' if modifier > 0 else ''}{modifier}"
            response += f"\n**Total: {result['total']}**"
            
            return [TextContent(type="text", text=response)]
        
        elif name == "roll_standard":
            die_type = arguments["die_type"]
            num_dice = arguments.get("num_dice", 1)
            modifier = arguments.get("modifier", 0)
            die_size = int(die_type[1:])  # Remove 'd' prefix
            
            result = dice_roller.roll_dice(num_dice, die_size, modifier)
            dice_roller.add_to_history("standard_roll", result)
            
            rolls_str = ", ".join(str(r) for r in result["rolls"])
            response = f"🎲 Rolling {result['notation']}:\n"
            response += f"Rolls: [{rolls_str}]"
            if modifier != 0:
                response += f" {'+' if modifier > 0 else ''}{modifier}"
            response += f"\n**Total: {result['total']}**"
            
            return [TextContent(type="text", text=response)]
        
        elif name == "roll_advantage":
            die_size = arguments.get("die_size", 20)
            modifier = arguments.get("modifier", 0)
            result = dice_roller.roll_with_advantage(die_size, modifier)
            dice_roller.add_to_history("advantage_roll", result)
            
            response = f"🎯 Rolling d{die_size} with ADVANTAGE:\n"
            response += f"Rolls: {result['rolls'][0]} and {result['rolls'][1]}\n"
            response += f"Keeping highest: {result['result']}"
            if modifier != 0:
                response += f" {'+' if modifier > 0 else ''}{modifier}"
            response += f"\n**Total: {result['total']}**"
            
            return [TextContent(type="text", text=response)]
        
        elif name == "roll_disadvantage":
            die_size = arguments.get("die_size", 20)
            modifier = arguments.get("modifier", 0)
            result = dice_roller.roll_with_disadvantage(die_size, modifier)
            dice_roller.add_to_history("disadvantage_roll", result)
            
            response = f"🎯 Rolling d{die_size} with DISADVANTAGE:\n"
            response += f"Rolls: {result['rolls'][0]} and {result['rolls'][1]}\n"
            response += f"Keeping lowest: {result['result']}"
            if modifier != 0:
                response += f" {'+' if modifier > 0 else ''}{modifier}"
            response += f"\n**Total: {result['total']}**"
            
            return [TextContent(type="text", text=response)]
        
        elif name == "roll_exploding":
            num_dice = arguments.get("num_dice", 1)
            die_size = arguments["die_size"]
            modifier = arguments.get("modifier", 0)
            result = dice_roller.roll_exploding_dice(num_dice, die_size, modifier)
            dice_roller.add_to_history("exploding_roll", result)
            
            response = f"💥 Rolling {result['notation']} (Exploding!):\n"
            for i, rolls in enumerate(result['all_rolls'], 1):
                if len(rolls) > 1:
                    response += f"Die {i}: {' → '.join(str(r) for r in rolls)} (exploded!)\n"
                else:
                    response += f"Die {i}: {rolls[0]}\n"
            
            response += f"Die totals: [{', '.join(str(r) for r in result['final_rolls'])}]"
            if modifier != 0:
                response += f" {'+' if modifier > 0 else ''}{modifier}"
            response += f"\n**Total: {result['total']}**"
            if result['exploded_count'] > 0:
                response += f"\n🎆 Dice exploded {result['exploded_count']} time(s)!"
            
            return [TextContent(type="text", text=response)]
        
        elif name == "roll_percentile":
            result = dice_roller.roll_percentile()
            dice_roller.add_to_history("percentile_roll", result)
            
            response = f"🎲 Rolling percentile die (d100):\n"
            response += f"Tens: {result['tens']}, Ones: {result['ones']}\n"
            response += f"**Result: {result['result']}**"
            
            return [TextContent(type="text", text=response)]
        
        elif name == "roll_fudge":
            num_dice = arguments.get("num_dice", 4)
            result = dice_roller.roll_fudge_dice(num_dice)
            dice_roller.add_to_history("fudge_roll", result)
            
            rolls_str = ", ".join(["+" if r == 1 else "-" if r == -1 else "0" for r in result["rolls"]])
            response = f"🎲 Rolling {result['notation']}:\n"
            response += f"Rolls: [{rolls_str}]\n"
            response += f"**Total: {result['total']}**"
            
            return [TextContent(type="text", text=response)]
        
        elif name == "get_history":
            limit = arguments.get("limit", 10)
            if not dice_roller.roll_history:
                return [TextContent(type="text", text="📜 No roll history available.")]
            
            recent_rolls = dice_roller.roll_history[-limit:]
            response = f"📜 Last {min(limit, len(recent_rolls))} rolls:\n\n"
            
            for i, entry in enumerate(reversed(recent_rolls), 1):
                timestamp = entry['timestamp'].split('T')[1].split('.')[0]  # Get time only
                roll_type = entry['type'].replace('_', ' ').title()
                result = entry['result']
                
                if isinstance(result, dict):
                    if 'total' in result:
                        response += f"{i}. [{timestamp}] {roll_type}: **{result['total']}**\n"
                    elif 'results' in result:
                        response += f"{i}. [{timestamp}] {roll_type}: {result['results']}\n"
                else:
                    response += f"{i}. [{timestamp}] {roll_type}: {result}\n"
            
            return [TextContent(type="text", text=response)]
        
        elif name == "clear_history":
            dice_roller.roll_history = []
            dice_roller.save_history()
            dice_roller.add_to_history("history_cleared", "History was cleared")
            return [TextContent(type="text", text="🗑️ Roll history has been cleared.")]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except ValueError as e:
        error_msg = f"❌ Validation Error: {str(e)}"
        logger.error(f"Validation error in tool {name}: {e}")
        return [TextContent(type="text", text=error_msg)]
    except KeyError as e:
        error_msg = f"❌ Missing Parameter: {str(e)}"
        logger.error(f"Missing parameter in tool {name}: {e}")
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        error_msg = f"❌ Unexpected Error: {str(e)}"
        logger.error(f"Unexpected error in tool {name}: {e}")
        return [TextContent(type="text", text=error_msg)]

async def main():
    """Main entry point for the server"""
    logger.info("Starting Dice Roller MCP Server")
    
    try:
        # Run the server using stdio transport
        async with stdio_server() as (read_stream, write_stream):
            logger.debug("Server streams created")
            server_task = asyncio.create_task(app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            ))
            logger.debug("Server task created")
            
            # Keep the main coroutine alive
            while True:
                await asyncio.sleep(3600)

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
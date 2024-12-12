import os
import random
import json
import logging
from typing import List, Dict, Union
import telegram
from telegram import Update, Poll
from telegram.ext import Application, CommandHandler, ContextTypes

import nest_asyncio
nest_asyncio.apply()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class QuizManager:
    """
    A comprehensive quiz management system that allows easy scaling and modification of quizzes.
    """
    def __init__(self, quiz_file_path: str = 'quizzes.json'):
        """
        Initialize QuizManager with a JSON file for storing quizzes.
        
        :param quiz_file_path: Path to the JSON file containing quizzes
        """
        self.quiz_file_path = quiz_file_path
        self.quizzes = self._load_quizzes()

    def _load_quizzes(self) -> Dict[str, List[Dict]]:
        """
        Load quizzes from a JSON file.
        
        :return: Dictionary of quizzes by category
        """
        try:
            with open(self.quiz_file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            # Create a default quiz structure if file doesn't exist
            default_quizzes = {
                'flutter': [],
                'linux': [],
                'cybersecurity': [],
                'web_development': [],
                'python': [],
                'general_programming': []
            }
            self._save_quizzes(default_quizzes)
            return default_quizzes

    def _save_quizzes(self, quizzes: Dict[str, List[Dict]]):
        """
        Save quizzes to the JSON file.
        
        :param quizzes: Dictionary of quizzes by category
        """
        with open(self.quiz_file_path, 'w', encoding='utf-8') as file:
            json.dump(quizzes, file, indent=2, ensure_ascii=False)

    def add_quiz(self, category: str, question: str, options: List[str], 
                 correct_option: str, explanation: str = None):
        """
        Add a new quiz question to a specific category.
        
        :param category: Quiz category
        :param question: Quiz question
        :param options: List of answer options
        :param correct_option: The correct answer
        :param explanation: Optional explanation for the correct answer
        """
        # Validate category exists
        if category not in self.quizzes:
            raise ValueError(f"Category '{category}' does not exist")

        # Create quiz entry
        quiz_entry = {
            "question": question,
            "options": options,
            "correct_option": correct_option,
            "explanation": explanation or "Great job or keep learning!"
        }

        # Add to quizzes
        self.quizzes[category].append(quiz_entry)
        
        # Save updated quizzes
        self._save_quizzes(self.quizzes)

    def get_random_quiz(self, category: str = None) -> Dict:
        """
        Get a random quiz question from a specific or random category.
        
        :param category: Optional specific category
        :return: A random quiz question
        """
        # If no category specified, choose a random one
        if not category:
            category = random.choice(list(self.quizzes.keys()))
        
        # Validate category
        if category not in self.quizzes:
            category = 'general_programming'
        
        # Get quizzes for the category
        category_quizzes = self.quizzes[category]
        
        # Return random quiz if quizzes exist
        if category_quizzes:
            return random.choice(category_quizzes)
        
        # Fallback to general programming if no quizzes in category
        return random.choice(self.quizzes['general_programming'])

    def get_categories(self) -> List[str]:
        """
        Get all available quiz categories.
        
        :return: List of quiz categories
        """
        return list(self.quizzes.keys())

class QuizGenerator:
    """
    A specialized Quiz Generator for Tech and Programming Channels
    """
    def __init__(self, bot_token: str, channels: List[str], groups: List[str], 
                 quiz_file_path: str = 'quizzes.json'):
        """
        Initialize the QuizGenerator with bot token, target chats, and quiz management.
        
        :param bot_token: Telegram bot token
        :param channels: List of channel usernames to post quizzes
        :param groups: List of group chat IDs to post quizzes
        :param quiz_file_path: Path to the quiz JSON file
        """
        self.bot_token = bot_token
        self.channels = channels
        self.groups = groups
        self.quiz_manager = QuizManager(quiz_file_path)

    async def send_quiz(self, bot: telegram.Bot, category: str = None):
        """
        Generate and send a quiz to all specified channels and groups.
        
        :param bot: Telegram Bot instance
        :param category: Quiz category to generate (optional)
        """
        try:
            # Get a random quiz
            quiz = self.quiz_manager.get_random_quiz(category)
            logger.info(f"Quiz not sent to channel:")

            # Prepare options for the poll
            poll_options = quiz['options']
            logger.info(f"Quiz  to channel: ")
            
            # Create a title that includes the category
            category = next(
                (cat for cat, quizzes in self.quiz_manager.quizzes.items() 
                 if quiz in quizzes), 
                'General Programming'
            )
            
            full_question = f"[{category.replace('_', ' ').title()}] {quiz['question']}"
            
            # Send to channels
            for channel in self.channels:
                try:
                    await bot.send_poll(
                        chat_id=channel,
                        question=full_question,
                        options=poll_options,
                        type=Poll.QUIZ,
                        correct_option_id=poll_options.index(quiz['correct_option']),
                        explanation=quiz.get('explanation', 'Great job or keep learning!'),
                        explanation_parse_mode='HTML'
                    )
                    logger.info(f"Quiz sent to channel: {channel}")
                except Exception as channel_error:
                    logger.error(f"Error sending quiz to channel {channel}: {channel_error}")
            
            # Send to groups
            for group in self.groups:
                try:
                    await bot.send_poll(
                        chat_id=group,
                        question=full_question,
                        options=poll_options,
                        type=Poll.QUIZ,
                        correct_option_id=poll_options.index(quiz['correct_option']),
                        explanation=quiz.get('explanation', 'Great job or keep learning!'),
                        explanation_parse_mode='HTML'
                    )
                    logger.info(f"Quiz sent to group: {group}")
                except Exception as group_error:
                    logger.error(f"Error sending quiz to group {group}: {group_error}")
        
        except Exception as e:
            logger.error(f"Error in send_quiz: {e}")

def main():
    """
    Main function to set up and run the Telegram Quiz Bot.
    """
    # Replace with your actual bot token
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7158191852:AAEYgUWeUbCVgWdm0yzZRAhL5tcGBMkoErc')
    
    # Replace with your actual channel and group usernames/IDs
    CHANNELS = [
        '@flutter_learning_free',
        '@Linux_learning_free', 
        '@web101_development_free',
        '@python_learning_free',
        '@firsend'
    ]
    
    GROUPS = [
        'techwithdilanchat',
    ]

    # Create quiz generator
    quiz_generator = QuizGenerator(BOT_TOKEN, CHANNELS, GROUPS, 'quizzes.json')

    # Optionally, add some initial quizzes if the file is empty
    quiz_manager = quiz_generator.quiz_manager
    
    # Example of how to add a quiz programmatically
    try:
        # Add a Flutter quiz with an explanation
        quiz_manager.add_quiz(
            category='flutter',
            question='What is the primary programming language used in Flutter?',
            options=['Java', 'Kotlin', 'Dart', 'Swift'],
            correct_option='Dart',
            explanation='Dart is the official programming language developed by Google for building Flutter applications. It provides excellent performance and supports both mobile and web platforms.'
        )
    except Exception as e:
        logger.warning(f"Initial quiz addition failed: {e}")

    # Set up application with custom configuration to handle conflicts
    application = Application.builder().token(BOT_TOKEN)\
        .concurrent_updates(True)\
        .rate_limiter(None)\
        .build()

    # Add error handler to log any unhandled errors
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, context.error)

    application.add_error_handler(error_handler)

    # Dynamic command handler generation
    def generate_quiz_handler(category=None):
        async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await quiz_generator.send_quiz(context.bot, category)
        return handler

    # Add base quiz command
    application.add_handler(CommandHandler("quiz", generate_quiz_handler()))

    # Dynamically generate commands for each category
    for category in quiz_generator.quiz_manager.get_categories():
        # Convert category to a valid command name
        command_name = f"{category.replace('_', '')}_quiz"
        application.add_handler(
            CommandHandler(command_name, generate_quiz_handler(category))
        )

    # Start the bot
    try:
        logger.info("Starting bot...")
        application.run_polling(
            drop_pending_updates=True,
            stop_signals=None
        )
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

if __name__ == '__main__':
    main()

# Required dependencies:
# pip install python-telegram-bot
# pip install nest_asyncio
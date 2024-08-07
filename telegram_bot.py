import sys
print(sys.version)

import mylibs.constants as constants
import mylibs.ngsi_ld_parking as ngsi_parking
import time

from landtransportsg import PublicTransport

import json
from requests.exceptions import RequestException, HTTPError
from ngsildclient import Client, Entity, SmartDataModels
from datetime import datetime

import logging
from geopy.distance import geodesic
from telegram import Update, ForceReply, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters, JobQueue

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def ngsi_test_fn():
    ret = ngsi_parking.geoquery_ngsi_point(input_type="Carpark", maxDistance=5000, lat=103.83359, long=1.3071)
    print(len(ret))

# State definitions
DESTINATION, LIVE_LOCATION = range(2)

# Store user data
user_data = {}

def find_closest_three_carparks(nearest_carparks_list, dest_lat, dest_long):
    closest_three_carparks = []
    for carpark in nearest_carparks_list:
        carpark_dict = carpark.to_dict()
        lat = carpark_dict["location"]["value"]["coordinates"][1]
        long = carpark_dict["location"]["value"]["coordinates"][0]
        distance = geodesic((dest_lat, dest_long), (lat, long)).km
        carpark_dict["distance"] = distance
        
        if carpark_dict["LotType"]["value"] == "C" and carpark_dict["ParkingAvalibility"]["value"] > 0:
            if len(closest_three_carparks) < 3:
                closest_three_carparks.append(carpark_dict)
            else:
                farthest_carpark = max(closest_three_carparks, key=lambda x: x["distance"])
                if farthest_carpark["distance"] > carpark_dict["distance"]:
                    closest_three_carparks.remove(farthest_carpark)
                    closest_three_carparks.append(carpark_dict)
    return closest_three_carparks

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask for destination location."""
    if update.message:
        await update.message.reply_text('Hi! Please share your destination location by sending your location using the location sharing feature.')
    return DESTINATION

async def destination(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the destination location and ask for live location."""
    if update.message and update.message.location:
        user = update.message.from_user
        destination_location = update.message.location
        user_data[user.id] = {
            'destination': (destination_location.latitude, destination_location.longitude),
            'notified_within_5km': False,
            'live_location': None
        }

        try:
            nearest_carparks = ngsi_parking.geoquery_ngsi_point(input_type="Carpark", maxDistance=1000, lat=destination_location.latitude, long=destination_location.longitude)

            if len(nearest_carparks) == 0:
                await update.message.reply_text("No nearby carparks found.")
            else:
                closest_three_carparks = find_closest_three_carparks(nearest_carparks_list=nearest_carparks, dest_lat=destination_location.latitude, dest_long=destination_location.longitude)

                closest_carparks_message = "The closest 3 carparks to your destination are:\n"
                for count, carpark in enumerate(closest_three_carparks, 1):
                    closest_carparks_message += (
                        f"{count}: \nArea: {carpark['DevelopmentName']['value']} \nLots: {carpark['ParkingAvalibility']['value']} \n"
                        f"Distance from destination: {carpark['distance']} km\n"
                    )

                await update.message.reply_text(closest_carparks_message)

            await update.message.reply_text('Got your destination. Now please share your live location continuously.')
            return LIVE_LOCATION
        except Exception as e:
            logger.error(f"Error fetching carparks: {e}")
            await update.message.reply_text('There was an error fetching nearby carparks. Please try again later.')
            return ConversationHandler.END
    else:
        await update.message.reply_text('Please send your destination location by using the location sharing feature in Telegram.')
        return DESTINATION

async def live_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the user's live location."""
    if update.message and update.message.location:
        user = update.message.from_user
        live_location = update.message.location

        if user.id in user_data:
            user_data[user.id]['live_location'] = (live_location.latitude, live_location.longitude)
            # Schedule the job to check location only after receiving the live location
            if 'job' not in user_data[user.id]:
                job = context.job_queue.run_repeating(check_location, interval=10, first=0, data=user.id)
                user_data[user.id]['job'] = job

    return LIVE_LOCATION

async def check_location(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Periodically check if the user is within 5km of their destination."""
    job = context.job
    user_id = job.data
    if user_id in user_data:
        destination = user_data[user_id].get('destination')
        live_location = user_data[user_id].get('live_location')

        if destination and live_location:
            distance = geodesic(destination, live_location).km

            if distance <= 5 and not user_data[user_id]['notified_within_5km']:
                user_data[user_id]['notified_within_5km'] = True
                context.bot.send_message(chat_id=user_id, text='You are within 5km of your destination!')

                try:
                    nearest_carparks = ngsi_parking.geoquery_ngsi_point(input_type="Carpark", maxDistance=1000, lat=destination[0], long=destination[1])
                    if len(nearest_carparks) == 0:
                        context.bot.send_message(chat_id=user_id, text="No nearby carparks found.")
                    else:
                        closest_three_carparks = find_closest_three_carparks(nearest_carparks_list=nearest_carparks, dest_lat=destination[0], dest_long=destination[1])

                        closest_carparks_message = "The current closest 3 carparks to your destination with available lots are:\n"
                        for count, carpark in enumerate(closest_three_carparks, 1):
                            closest_carparks_message += (
                                f"{count}: \nArea: {carpark['DevelopmentName']['value']} \nLots: {carpark['ParkingAvalibility']['value']} \n"
                                f"Distance from destination: {carpark['distance']} km\n"
                            )
                        context.bot.send_message(chat_id=user_id, text=closest_carparks_message)
                except Exception as e:
                    logger.error(f"Error fetching carparks: {e}")
                    context.bot.send_message(chat_id=user_id, text='There was an error fetching nearby carparks. Please try again later.')
            elif distance > 5:
                user_data[user_id]['notified_within_5km'] = False
                context.bot.send_message(chat_id=user_id, text='Not within 5km of destination yet')

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    if update.message:
        await update.message.reply_text('Bye! Hope to talk to you again soon.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    application = ApplicationBuilder().token(constants.TELEGRAM_BOT_KEY).build()

    job_queue = application.job_queue

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            DESTINATION: [MessageHandler(filters.LOCATION | filters.TEXT, destination)],
            LIVE_LOCATION: [MessageHandler(filters.LOCATION, live_location)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == '__main__':
    main()

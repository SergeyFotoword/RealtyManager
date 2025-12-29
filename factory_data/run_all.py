from factory_data.factory_data_accounts import run as run_accounts
from factory_data.factory_data_locations import run as run_locations
from factory_data.factory_data_properties import run as run_properties
from factory_data.factory_data_listings import run as run_listings
from factory_data.factory_data_bookings import run as run_bookings
from factory_data.factory_data_reviews import run as run_reviews


def run():
    print("=== START DATABASE SEEDING ===")

    print("\n[1/6] Accounts")
    run_accounts()

    print("\n[2/6] Locations")
    run_locations()

    print("\n[3/6] Properties")
    run_properties()

    print("\n[4/6] Listings")
    run_listings()

    print("\n[5/6] Bookings")
    run_bookings()

    print("\n[6/6] Reviews")
    run_reviews()

    print("\n=== DONE ===")
from apps.listings.models.listing_view import ListingView

def track_listing_view(*, listing, user=None):
    ListingView.objects.create(listing=listing, user=user if user and user.is_authenticated else None)
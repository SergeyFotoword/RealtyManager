class ListingOrderBy:
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    CREATED_NEW = "created_new"
    CREATED_OLD = "created_old"

    POPULAR = "popular"
    POPULAR_UNIQ = "popular_uniq"
    POPULAR_7D = "popular_7d"
    POPULAR_30D = "popular_30d"

    ALL = {
        PRICE_ASC,
        PRICE_DESC,
        CREATED_NEW,
        CREATED_OLD,
        POPULAR,
        POPULAR_UNIQ,
        POPULAR_7D,
        POPULAR_30D,
    }
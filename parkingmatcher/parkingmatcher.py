# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import sqlite3

parking_zones = {"etap1": "I Etap",
                 "etap2": "II Etap",
                 "outside": "na zewnątrz"}

datehour_format = "%Y-%m-%dT%H"


def date_hour(source):
    if isinstance(source, datetime):
        return datetime(source.year, source.month, source.day, source.hour)
    else:
        return datetime.strptime(source.strip()[:13], datehour_format)


class User:
    def __init__(self, name, email):
        """
        A user
        Will probably also include password and some settings flag (like notification settings)
        :param name: Display name of the user
        :param email: User email
        """
        self.name = name
        self.email = email

    def __repr__(self):
        return "{0} <{1}>".format(self.name, self.email)

    def __eq__(self, other):
        if other is None or not isinstance(other, User):
            return False
        return self.email == other.email


class Spot:
    def __init__(self, zone, place, owner):
        """
        A parking spot
        :param zone: zone id, as listed in `zones` dictionary
        :param place: spot number, not really stored as number
        :param owner: User object of the spot's owner.
        """
        if zone not in parking_zones:
            raise AttributeError("zone '%s' not one of the zones" % zone)
        if not isinstance(owner, User):
            raise AttributeError("owner is not of type User")
        self.zone = zone
        self.place = str(place)
        self.owner = owner

    def __repr__(self):
        return "{1} m. {0} nal. do {2}".format(self.place, parking_zones[self.zone], self.owner.name)

    def __eq__(self, other):
        if other is None or not isinstance(other, Spot):
            return False
        return self.place == other.place and self.zone == other.zone


class Period:
    def __init__(self, begins, ends):
        time1 = date_hour(begins)
        time2 = date_hour(ends)
        self.begin = time1 if time1 < time2 else time2
        self.end = time2 if time1 < time2 else time1

    def __repr__(self):
        return "<{0} - {1}>".format(self.begin.strftime(datehour_format), self.end.strftime(datehour_format))

    def __eq__(self, other):
        if other is None or not isinstance(other, Period):
            return False
        return self.begin == other.begin and self.end == other.end

    def length(self):
        return abs(self.end - self.begin).total_seconds() / 3600

    def contains(self, other):
        return other.begin >= self.begin and other.end <= self.end

    def intersects(self, other):
        return other.end > self.begin and other.begin < self.end

    def adjacent(self, other):
        return self.end == other.begin or self.begin == other.end

    def gluable(self, other):
        return self.adjacent(other) or self.intersects(other)

    def intersection(self, other):
        return None if other.end <= self.begin or other.begin >= self.end else Period(max(self.begin, other.begin),
                                                                                      min(self.end, other.end))

    def before(self, other):
        return None if other.begin <= self.begin else Period(self.begin, min(self.end, other.begin))

    def after(self, other):
        return None if other.end >= self.end else Period(max(other.end, self.begin), self.end)

    def glue(self, other):
        if self.gluable(other):
            return Period(min(self.begin, other.begin), max(self.end, other.end))


class Offer:
    __match = None  # a matchingRequest will be put here

    def __init__(self, spot, period, matching_request=None):
        """
        An offer of a free parking spot
        :param spot: The spot that will be empty...
        :param time_begins: ...from this time (passed as a DateTime object or ISO8601 string)...
        :param time_ends: ...to this time (passed as a DateTime object or ISO8601 string)
        """
        if not isinstance(spot, Spot):
            raise AttributeError("spot is not of type Spot")
        self.spot = spot
        self.period = period
        self.__match = matching_request

    @classmethod
    def matched_with(cls, spot, matching_request):
        return cls(spot, matching_request.period, matching_request)

    @classmethod
    def unmatched(cls, spot, period):
        return cls(spot, period)

    def __repr__(self):
        return "{0} wolne od {1} do {2}{3}".format(self.spot,
                                                   self.period.begin.strftime("%d.%m.%Y g. %H"),
                                                   self.period.end.strftime("%d.%m.%Y g. %H"),
                                                   ("reserved for %s" % self.__match.requestor.name)
                                                   if self.__match else "")

    def __eq__(self, other):
        if other is None or not isinstance(other, Offer):
            return False
        return self.spot == other.spot and self.period == other.period and self.__match == other.__match

    def matched_request(self):
        return self.__match


class Request:
    def __init__(self, requestor, time_begins, time_ends, in_zones, when_requested=datetime.now()):
        """
        A request for an empty spot
        :param requestor: Who is requesting a spot...
        :param time_begins: ...from this time (passed as a DateTime object or ISO8601 string)...
        :param time_ends: ...to this time (passed as a DateTime object or ISO8601 string)
        :param in_zones: ...in these zones, comma-delimited or passed as string list
        :param when_requested: Time of request. Defaults to now.
        """
        if not isinstance(requestor, User):
            raise AttributeError("requestor is not of type User")
        self.requestor = requestor
        self.period = Period(time_begins, time_ends)
        self.zones = list(filter(lambda z: z in parking_zones,
                                 map(lambda z: z.strip(),
                                     in_zones if isinstance(in_zones, list) else in_zones.split(","))))
        self.when_requested = when_requested

    def matches(self, offer):
        return offer.spot.zone in self.zones and offer.period.contains(self.period)

    def __eq__(self, other):
        if other is None or not isinstance(other, Request):
            return False
        return self.requestor == other.requestor and self.period == other.period and self.zones == other.zones

    def __repr__(self):
        return "{0} szuka miejsca w {1} od {2} do {3}".format(self.requestor.name,
                                                              ", ".join(self.zones),
                                                              self.period.begin.strftime("%d.%m.%Y g. %H"),
                                                              self.period.end.strftime("%d.%m.%Y g. %H"))


class TestDataAccess:
    __offers = []
    __request_queue = []

    def __init__(self, init_users, init_spots):
        self.users = init_users
        self.spots = init_spots

    def clear(self):
        self.__offers = []
        self.__request_queue = []

    def get_request_queue(self, user=None, before=None):
        zones = {spot.zone for spot in filter(lambda s: s.owner == user, self.spots)} if user else None
        return [req for req in filter(lambda r: r.period.end < before if before else True, self.__request_queue)
                if zones is None or zones & set(req.zones)]

    def get_matched_requests(self):
        return [off.matched_request() for off in self.__offers if off.matched_request()]

    def get_unmatched_offers(self):
        return list(filter(lambda o: o.matched_request() is None, self.__offers))

    def get_matched_offers(self):
        return list(filter(lambda o: o.matched_request(), self.__offers))

    def get_offers_for_spot(self, spot, since=None, until=None):
        return sorted(filter(lambda off: off.spot == spot
                             and (off.period.begin == since if since else True)
                             and (off.period.end == until if until else True),
                             self.__offers),
                      key=lambda off: off.period.begin)

    def add_offer(self, offer):
        self.__offers.append(offer)

    def delete_offer(self, offer):
        if offer in self.__offers:
            self.__offers.remove(offer)

    def add_request(self, request):
        self.__request_queue.append(request)

    def delete_request_from_queue(self, request):
        if request in self.__request_queue:
            self.__request_queue.remove(request)


class DBDataAccess:
    query_users = "select * from user"
    query_spots = "select rowid, * from spot"
    query_requests = "select rowid, * from request"
    query_offers = "select rowid, * from offer"
    query_offers_with_data = "select o.timebegins, o.timeends, s.zone, s.number, u.name, u.email from offer o " \
                             "left join spot s on (o.spotid = s.rowid) " \
                             "left join user u on (u.email = s.owneremail)"
    query_match = "select rowid, * from spot"

    def __init__(self, dbfile):
        self.dbcon = sqlite3.connect(dbfile)
        self.cursor = self.dbcon.cursor()

    def __del__(self):
        self.dbcon.close()


class Api:
    def __init__(self, data):
        self.data = data

    def __match_request_with_offer(self, request, offer):
        self.data.add_offer(Offer.matched_with(offer.spot, request))
        for per in [offer.period.before(request.period), offer.period.after(request.period)]:
            if per is not None:
                self.data.add_offer(Offer.unmatched(offer.spot, per))
        self.data.delete_request_from_queue(request)
        self.data.delete_offer(offer)

    def new_offer(self, offer):
        # disallow new offers over existing matched ones
        existing_offers = list(filter(lambda off: off.period.gluable(offer.period),
                                      self.data.get_offers_for_spot(offer.spot)))
        if any(filter(lambda off: off.period.intersects(offer.period) and off.matched_request(), existing_offers)):
            return

        for xo in existing_offers:
            offer = Offer.unmatched(offer.spot, offer.period.glue(xo.period))
            self.data.delete_offer(xo)

        matching_requests = list(filter(lambda req: req.matches(offer), self.data.get_request_queue()))
        if any(matching_requests):
            first_request = min(matching_requests, key=lambda req: req.when_requested)
            self.__match_request_with_offer(first_request, offer)
        else:
            self.data.add_offer(offer)

    def cancel_offer(self, offer):
        matching_offers = self.data.get_offers_for_spot(offer.spot, offer.period.begin, offer.period.end)
        for matching in matching_offers:
            req = matching.matched_request()
            self.data.delete_offer(matching)
            if req:
                self.new_request(req)

    def new_request(self, request):
        # check for existing requests, expand if necessary
        matching_offers = list(filter(lambda off: request.matches(off), self.data.get_unmatched_offers()))
        if any(matching_offers):
            first_offer = min(matching_offers, key=lambda off: off.period.length())
            self.__match_request_with_offer(request, first_offer)
        else:
            self.data.add_request(request)

    def cancel_request(self, request):
        if request in self.data.get_request_queue():
            self.data.delete_request_from_queue(request)
        else:
            matched_offer = list(filter(lambda off: off.matched_request() == request, self.data.get_matched_offers()))
            for offer in matched_offer:
                self.data.delete_offer(offer)
                self.new_offer(Offer.unmatched(offer.spot, offer.period))

    def get_request_for_owner(self, owner, until=date_hour(datetime.now() + timedelta(days=7))):
        return self.data.get_request_queue(owner, until)


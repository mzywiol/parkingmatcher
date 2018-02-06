import unittest
from parkingmatcher.parkingmatcher import *


def today(h):
    return date_hour("2018-01-02T%s" % str(h))


def tomorrow(h):
    return date_hour("2018-01-03T%s" % str(h))


def hours(_from, _to):
    return Period(today(_from) if _from < 24 else tomorrow(_from - 24),
                  today(_to) if _to < 24 else tomorrow(_to - 24))


class UtilTest(unittest.TestCase):
    expected = datetime(2018, 1, 2, 3, 0, 0, 0, None)

    def test_datehour_from_string(self):
        self.assertEqual(self.expected, date_hour(today(3)))
        self.assertEqual(self.expected, date_hour("2018-01-02T03:04"))
        self.assertEqual(self.expected, date_hour(" 2018-01-02T03:04"))

    def test_datehour_from_datetime(self):
        self.assertEqual(self.expected, date_hour(datetime(2018, 1, 2, 3)))
        self.assertEqual(self.expected, date_hour(datetime(2018, 1, 2, 3, 4)))
        self.assertEqual(self.expected, date_hour(datetime(2018, 1, 2, 3, 4, 5, 6)))
        self.assertEqual(self.expected, date_hour(datetime(2018, 1, 2, 3, 4, 5)))


class PeriodTest(unittest.TestCase):
    def test_length(self):
        self.assertEqual(3, hours(3, 6).length())
        self.assertEqual(3, hours(6, 3).length())
        self.assertEqual(27, hours(3, 30).length())
        self.assertEqual(21, hours(27, 6).length())

    def test_contains(self):
        two_to_five = hours(2, 5)
        self.assertTrue(two_to_five.contains(hours(2, 5)))
        self.assertTrue(two_to_five.contains(hours(3, 4)))
        self.assertTrue(two_to_five.contains(hours(3, 5)))
        self.assertTrue(two_to_five.contains(hours(2, 4)))
        self.assertTrue(two_to_five.contains(hours(2, 2)))
        self.assertTrue(two_to_five.contains(hours(5, 5)))
        self.assertFalse(two_to_five.contains(hours(0, 1)))
        self.assertFalse(two_to_five.contains(hours(0, 2)))
        self.assertFalse(two_to_five.contains(hours(0, 3)))
        self.assertFalse(two_to_five.contains(hours(0, 5)))
        self.assertFalse(two_to_five.contains(hours(0, 6)))
        self.assertFalse(two_to_five.contains(hours(4, 6)))
        self.assertFalse(two_to_five.contains(hours(5, 6)))
        self.assertFalse(two_to_five.contains(hours(6, 7)))

    def test_adjacent(self):
        two_to_five = hours(2, 5)
        self.assertFalse(two_to_five.adjacent(hours(2, 5)))
        self.assertFalse(two_to_five.adjacent(hours(3, 4)))
        self.assertFalse(two_to_five.adjacent(hours(3, 5)))
        self.assertFalse(two_to_five.adjacent(hours(2, 4)))
        self.assertTrue(two_to_five.adjacent(hours(2, 2)))
        self.assertTrue(two_to_five.adjacent(hours(5, 5)))
        self.assertFalse(two_to_five.adjacent(hours(0, 1)))
        self.assertTrue(two_to_five.adjacent(hours(0, 2)))
        self.assertFalse(two_to_five.adjacent(hours(0, 3)))
        self.assertFalse(two_to_five.adjacent(hours(0, 5)))
        self.assertFalse(two_to_five.adjacent(hours(0, 6)))
        self.assertFalse(two_to_five.adjacent(hours(4, 6)))
        self.assertTrue(two_to_five.adjacent(hours(5, 6)))
        self.assertFalse(two_to_five.adjacent(hours(6, 7)))

    def test_intersect(self):
        two_to_five = hours(2, 5)
        self.assertTrue(two_to_five.intersection(two_to_five))
        self.assertFalse(two_to_five.intersection(hours(0, 1)))
        self.assertFalse(two_to_five.intersection(hours(0, 2)))
        self.assertFalse(two_to_five.intersection(hours(5, 7)))
        self.assertFalse(two_to_five.intersection(hours(6, 7)))
        self.assertTrue(two_to_five.intersection(hours(0, 3)))
        self.assertTrue(two_to_five.intersection(hours(0, 5)))
        self.assertTrue(two_to_five.intersection(hours(1, 6)))
        self.assertTrue(two_to_five.intersection(hours(2, 6)))
        self.assertTrue(two_to_five.intersection(hours(4, 6)))

    def test_intersection(self):
        two_to_five = hours(2, 5)
        self.assertEqual(two_to_five.intersection(two_to_five), two_to_five)
        self.assertIsNone(two_to_five.intersection(hours(0, 1)))
        self.assertIsNone(two_to_five.intersection(hours(0, 2)))
        self.assertIsNone(two_to_five.intersection(hours(5, 7)))
        self.assertIsNone(two_to_five.intersection(hours(6, 7)))
        self.assertEqual(two_to_five.intersection(hours(0, 3)), hours(2, 3))
        self.assertEqual(two_to_five.intersection(hours(0, 5)), two_to_five)
        self.assertEqual(two_to_five.intersection(hours(1, 6)), two_to_five)
        self.assertEqual(two_to_five.intersection(hours(2, 6)), two_to_five)
        self.assertEqual(two_to_five.intersection(hours(4, 6)), hours(4, 5))

    def test_before(self):
        two_to_five = hours(2, 5)
        self.assertEqual(two_to_five.before(hours(6, 7)), two_to_five)
        self.assertEqual(two_to_five.before(hours(5, 7)), two_to_five)
        self.assertEqual(two_to_five.before(hours(4, 7)), hours(2, 4))
        self.assertIsNone(two_to_five.before(hours(2, 7)))
        self.assertIsNone(two_to_five.before(hours(1, 7)))

    def test_after(self):
        two_to_five = hours(2, 5)
        self.assertEqual(two_to_five.after(hours(0, 1)), two_to_five)
        self.assertEqual(two_to_five.after(hours(0, 2)), two_to_five)
        self.assertEqual(two_to_five.after(hours(0, 3)), hours(3, 5))
        self.assertIsNone(two_to_five.after(hours(0, 5)))
        self.assertIsNone(two_to_five.after(hours(0, 6)))

    def test_gluable(self):
        two_to_five = hours(2, 5)
        self.assertTrue(two_to_five.gluable(hours(2, 5)))
        self.assertTrue(two_to_five.gluable(hours(3, 4)))
        self.assertTrue(two_to_five.gluable(hours(3, 5)))
        self.assertTrue(two_to_five.gluable(hours(2, 4)))
        self.assertTrue(two_to_five.gluable(hours(2, 2)))
        self.assertTrue(two_to_five.gluable(hours(5, 5)))
        self.assertFalse(two_to_five.gluable(hours(0, 1)))
        self.assertTrue(two_to_five.gluable(hours(0, 2)))
        self.assertTrue(two_to_five.gluable(hours(0, 3)))
        self.assertTrue(two_to_five.gluable(hours(0, 5)))
        self.assertTrue(two_to_five.gluable(hours(0, 6)))
        self.assertTrue(two_to_five.gluable(hours(4, 6)))
        self.assertTrue(two_to_five.gluable(hours(5, 6)))
        self.assertFalse(two_to_five.gluable(hours(6, 7)))

    def test_glue(self):
        self.assertIsNone(hours(1, 2).glue(hours(3, 4)))
        self.assertIsNone(hours(3, 4).glue(hours(1, 2)))
        self.assertEqual(hours(1, 2).glue(hours(2, 3)), hours(1, 3))
        self.assertEqual(hours(2, 3).glue(hours(1, 2)), hours(1, 3))
        self.assertEqual(hours(1, 3).glue(hours(2, 4)), hours(1, 4))
        self.assertEqual(hours(2, 4).glue(hours(1, 3)), hours(1, 4))


class SpotTest(unittest.TestCase):
    def test_wrong_zone(self):
        spot = None
        try:
            zone = "nosuch"
            spot = Spot(zone, "1", User("test", "test"))
            self.fail("Should raise AttributeError for wrong zone: '%s'" % zone)
        except AttributeError as e:
            self.assertEqual(e.args[0], "zone 'nosuch' not one of the zones")
            self.assertIsNone(spot)

    def test_not_a_user(self):
        spot = None
        try:
            spot = Spot("etap1", "1", "user")
            self.fail("Should raise AttributeError for owner not of User type")
        except AttributeError as e:
            self.assertEqual(e.args[0], "owner is not of type User")
            self.assertIsNone(spot)


class RequestTest(unittest.TestCase):
    def test_filter_zones(self):
        request = Request(User("test", "test"), "2018-01-01T01", "2018-01-01T01", ["etap1", "nosuch"])
        self.assertEqual(request.zones, ["etap1"])
        request = Request(User("test", "test"), "2018-01-01T01", "2018-01-01T01", "nosuch,etap2")
        self.assertEqual(request.zones, ["etap2"])
        request = Request(User("test", "test"), "2018-01-01T01", "2018-01-01T01", " outside , nosuch")
        self.assertEqual(request.zones, ["outside"])


user_e1 = User("e1only", "e1only@lp.pl")
user_e2 = User("e2only", "e2only@lp.pl")
user_oute2 = User("oute2", "oe2@lp.pl")
user_nopark = User("nopark", "nopark@lp.pl")

spot_e11 = Spot("etap1", 1, user_e1)
spot_e21 = Spot("etap2", 1, user_e2)
spot_e22 = Spot("etap2", 2, user_oute2)
spot_out1 = Spot("outside", 1, user_oute2)

api_test_data = TestDataAccess([user_e1, user_e2, user_oute2, user_nopark], [spot_e11, spot_e21, spot_e22, spot_out1])
api = Api(api_test_data)


class ApiTest(unittest.TestCase):
    def tearDown(self):
        api_test_data.clear()

    def assertListEqualContents(self, list1, list2):
        self.assertEqual(len(list1), len(list2))
        self.assertTrue(all(map(lambda e: e in list1, list2)))
        self.assertTrue(all(map(lambda e: e in list2, list1)))

    def test_new_offer_no_requests(self):
        # given
        self.assertEqual(len(api_test_data.get_request_queue()), 0)
        # when
        unmatched = Offer.unmatched(spot_e11, hours(3, 12))
        api.new_offer(unmatched)
        # then
        self.assertEqual(api_test_data.get_unmatched_offers(), [unmatched])
        self.assertEqual(api_test_data.get_matched_offers(), [])

    def test_new_offer_none_matching(self):
        # given
        api.new_request(Request(user_nopark, today(2), today(6), "etap1"))
        api.new_request(Request(user_nopark, today(10), today(16), "etap1"))
        api.new_request(Request(user_nopark, today(4), today(12), "etap2"))
        self.assertEqual(len(api_test_data.get_request_queue()), 3)
        # when
        unmatched = Offer.unmatched(spot_e11, hours(5, 11))
        api.new_offer(unmatched)
        # then
        self.assertEqual(api_test_data.get_unmatched_offers(), [unmatched])
        self.assertEqual(api_test_data.get_matched_offers(), [])
        self.assertEqual(len(api_test_data.get_request_queue()), 3)

    def test_new_offer_matching(self):
        # given
        api.new_request(Request(user_nopark, today(3), today(9), "etap2"))
        expected = Request(user_nopark, today(5), today(11), "etap2")
        api.new_request(expected)
        self.assertEqual(len(api_test_data.get_request_queue()), 2)
        # when
        api.new_offer(Offer.unmatched(spot_e21, hours(4, 12)))
        # then
        self.assertEqual(len(api_test_data.get_matched_offers()), 1)
        self.assertEqual(api_test_data.get_matched_offers()[0].matched_request(), expected)
        expected_unmatched = [Offer.unmatched(spot_e21, hours(4, 5)), Offer.unmatched(spot_e21, hours(11, 12))]
        self.assertListEqualContents(api_test_data.get_unmatched_offers(), expected_unmatched)
        self.assertEqual(len(api_test_data.get_request_queue()), 1)

    def test_disallow_new_offer_over_matched(self):
        # given
        api.new_offer(Offer.unmatched(spot_e21, hours(5, 9)))
        api.new_request(Request(user_nopark, today(5), today(9), "etap2"))
        self.assertEqual(len(api_test_data.get_matched_offers()), 1)
        self.assertEqual(len(api_test_data.get_request_queue()), 0)
        self.assertEqual(len(api_test_data.get_unmatched_offers()), 0)
        # when
        api.new_offer(Offer.unmatched(spot_e21, hours(2, 6)))
        api.new_offer(Offer.unmatched(spot_e21, hours(4, 9)))
        api.new_offer(Offer.unmatched(spot_e21, hours(4, 12)))
        api.new_offer(Offer.unmatched(spot_e21, hours(5, 12)))
        api.new_offer(Offer.unmatched(spot_e21, hours(6, 12)))
        api.new_offer(Offer.unmatched(spot_e21, hours(6, 8)))
        # then
        self.assertEqual(len(api_test_data.get_unmatched_offers()), 0)

    def test_new_offer_expanding(self):
        # given
        api.new_offer(Offer.unmatched(spot_e11, hours(1, 2)))
        api.new_offer(Offer.unmatched(spot_e21, hours(1, 3)))
        api.new_offer(Offer.unmatched(spot_e22, hours(2, 4)))
        api.new_offer(Offer.unmatched(spot_out1, hours(3, 4)))
        api.new_offer(Offer.unmatched(spot_e11, hours(6, 9)))
        api.new_offer(Offer.unmatched(spot_e21, hours(6, 9)))
        api.new_offer(Offer.unmatched(spot_e22, hours(6, 9)))
        api.new_offer(Offer.unmatched(spot_out1, hours(6, 9)))
        self.assertEqual(len(api_test_data.get_unmatched_offers()), 8)
        # when
        api.new_offer(Offer.unmatched(spot_e11, hours(2, 3)))
        api.new_offer(Offer.unmatched(spot_e21, hours(2, 4)))
        api.new_offer(Offer.unmatched(spot_e22, hours(1, 3)))
        api.new_offer(Offer.unmatched(spot_out1, hours(2, 3)))
        api.new_offer(Offer.unmatched(spot_e11, hours(5, 10)))
        api.new_offer(Offer.unmatched(spot_e21, hours(5, 9)))
        api.new_offer(Offer.unmatched(spot_e22, hours(6, 10)))
        api.new_offer(Offer.unmatched(spot_out1, hours(7, 8)))
        # then
        self.assertListEqualContents(api_test_data.get_unmatched_offers(),
                                     [Offer.unmatched(spot_e11, hours(1, 3)),
                                      Offer.unmatched(spot_e21, hours(1, 4)),
                                      Offer.unmatched(spot_e22, hours(1, 4)),
                                      Offer.unmatched(spot_out1, hours(2, 4)),
                                      Offer.unmatched(spot_e11, hours(5, 10)),
                                      Offer.unmatched(spot_e21, hours(5, 9)),
                                      Offer.unmatched(spot_e22, hours(6, 10)),
                                      Offer.unmatched(spot_out1, hours(6, 9))])

    def test_offer_expansion_matches_request(self):
        # given
        api.new_offer(Offer.unmatched(spot_e21, hours(3, 6)))
        api.new_request(Request(user_nopark, today(4), today(7), spot_e21.zone))
        self.assertEqual(len(api_test_data.get_matched_offers()), 0)
        self.assertEqual(len(api_test_data.get_request_queue()), 1)
        # when
        api.new_offer(Offer.unmatched(spot_e21, hours(6, 7)))
        # then
        self.assertEqual(len(api_test_data.get_matched_offers()), 1)
        self.assertEqual(len(api_test_data.get_request_queue()), 0)

    def test_new_offer_matching_multiple(self):
        # given
        later = date_hour(today(3))
        api.new_request(Request(user_nopark, today(4), today(10), "etap2", later))
        earlier = date_hour(today(2))
        expected = Request(user_nopark, today(5), today(11), "etap2", earlier)
        api.new_request(expected)
        self.assertEqual(len(api_test_data.get_request_queue()), 2)
        # when
        api.new_offer(Offer.unmatched(spot_e21, hours(4, 12)))
        # then
        self.assertEqual(api_test_data.get_matched_offers()[0].matched_request(), expected)
        self.assertListEqualContents(api_test_data.get_unmatched_offers(),
                                     [Offer.unmatched(spot_e21, hours(4, 5)), Offer.unmatched(spot_e21, hours(11, 12))])
        self.assertEqual(len(api_test_data.get_request_queue()), 1)

    def test_new_request_no_offers(self):
        # given
        self.assertEqual(len(api_test_data.get_unmatched_offers()), 0)
        # when
        unmatched = Request(user_nopark, today(2), today(6), "etap1")
        api.new_request(unmatched)
        # then
        self.assertEqual(api_test_data.get_request_queue(), [unmatched])
        self.assertEqual(api_test_data.get_matched_offers(), [])

    def test_new_request_none_matching(self):
        # given
        api.new_offer(Offer.unmatched(spot_e11, hours(2, 4)))
        api.new_offer(Offer.unmatched(spot_e11, hours(5, 8)))
        api.new_offer(Offer.unmatched(spot_e21, hours(2, 10)))
        api.new_offer(Offer.unmatched(spot_out1, hours(3, 12)))
        self.assertEqual(len(api_test_data.get_unmatched_offers()), 4)
        # when
        unmatched = Request(user_nopark, today(3), today(6), spot_e11.zone)
        api.new_request(unmatched)
        # then
        self.assertEqual(api_test_data.get_request_queue(), [unmatched])
        self.assertEqual(api_test_data.get_matched_offers(), [])

    def test_new_request_matching(self):
        # given
        api.new_offer(Offer.unmatched(spot_e11, hours(2, 4)))
        api.new_offer(Offer.unmatched(spot_e21, hours(2, 10)))
        self.assertEqual(len(api_test_data.get_unmatched_offers()), 2)
        # when
        request = Request(user_nopark, today(3), today(6), spot_e21.zone)
        api.new_request(request)
        # then
        self.assertEqual(len(api_test_data.get_request_queue()), 0)
        self.assertEqual(api_test_data.get_matched_offers(), [Offer.matched_with(spot_e21, request)])
        self.assertListEqualContents(api_test_data.get_unmatched_offers(),
                                     [Offer.unmatched(spot_e11, hours(2, 4)), Offer.unmatched(spot_e21, hours(2, 3)),
                                      Offer.unmatched(spot_e21, hours(6, 10))])

    def test_new_request_matching_multiple(self):
        # given
        api.new_offer(Offer.unmatched(spot_e22, hours(2, 10)))
        api.new_offer(Offer.unmatched(spot_e11, hours(2, 4)))
        api.new_offer(Offer.unmatched(spot_e21, hours(3, 6)))
        self.assertEqual(len(api_test_data.get_unmatched_offers()), 3)
        # when
        request = Request(user_nopark, today(3), today(6), spot_e21.zone)
        api.new_request(request)
        # then
        self.assertEqual(len(api_test_data.get_request_queue()), 0)
        self.assertEqual(api_test_data.get_matched_offers(), [Offer.matched_with(spot_e21, request)])
        self.assertListEqualContents(api_test_data.get_unmatched_offers(),
                                     [Offer.unmatched(spot_e22, hours(2, 10)), Offer.unmatched(spot_e11, hours(2, 4))])

    def test_get_offers_user_can_help_with(self):
        # given
        req_etap1 = Request(user_nopark, today(4), today(6), spot_e11.zone)
        req_etap12 = Request(user_nopark, today(7), today(9), [spot_e21.zone, spot_e11.zone])
        req_etap2 = Request(user_nopark, today(12), today(14), spot_e22.zone)
        req_outside = Request(user_nopark, tomorrow(4), tomorrow(8), spot_out1.zone)
        req_etap2_or_outside = Request(user_nopark, tomorrow(10), tomorrow(14), [spot_e21.zone, spot_out1.zone])
        req_far_future = Request(user_nopark, today(4) + timedelta(days=8), today(6) + timedelta(days=8), spot_e11.zone)
        for req in [req_etap1, req_etap12, req_etap2, req_etap2_or_outside, req_outside, req_far_future]:
            api.new_request(req)
        # when
        week_future = today(0) + timedelta(days=7)
        for_user_e1 = api.get_request_for_owner(user_e1, week_future)
        for_user_e2 = api.get_request_for_owner(user_e2, week_future)
        for_user_e2out = api.get_request_for_owner(user_oute2, week_future)
        # then
        self.assertListEqualContents(for_user_e1, [req_etap1, req_etap12])
        self.assertListEqualContents(for_user_e2, [req_etap12, req_etap2, req_etap2_or_outside])
        self.assertListEqualContents(for_user_e2out, [req_etap12, req_etap2, req_etap2_or_outside, req_outside])

    def test_delete_offer(self):
        # given
        unmatched = Offer.unmatched(spot_e21, hours(3, 6))
        api.new_offer(unmatched)
        self.assertEqual(len(api_test_data.get_unmatched_offers()), 1)
        # when
        api.cancel_offer(unmatched)
        # then
        self.assertEqual(len(api_test_data.get_unmatched_offers()), 0)

    def test_dont_delete_non_matching_offer(self):
        # given
        unmatched = Offer.unmatched(spot_e21, hours(3, 6))
        api.new_offer(unmatched)
        self.assertEqual(len(api_test_data.get_unmatched_offers()), 1)
        # when
        api.cancel_offer(Offer.unmatched(spot_e21, hours(0, 1)))
        api.cancel_offer(Offer.unmatched(spot_e21, hours(0, 3)))
        api.cancel_offer(Offer.unmatched(spot_e21, hours(0, 5)))
        api.cancel_offer(Offer.unmatched(spot_e21, hours(0, 6)))
        api.cancel_offer(Offer.unmatched(spot_e21, hours(4, 6)))
        api.cancel_offer(Offer.unmatched(spot_e21, hours(4, 8)))
        api.cancel_offer(Offer.unmatched(spot_e22, hours(3, 6)))
        self.assertEqual(api_test_data.get_unmatched_offers(), [unmatched])

    def test_delete_matched_offer(self):
        # given
        api.new_request(Request(user_nopark, today(3), today(6), spot_e11.zone))
        matched = Offer.unmatched(spot_e11, hours(3, 6))
        api.new_offer(matched)
        self.assertEqual(len(api_test_data.get_request_queue()), 0)
        self.assertEqual(len(api_test_data.get_matched_offers()), 1)
        # when
        api.cancel_offer(matched)
        # then
        self.assertEqual(len(api_test_data.get_matched_offers()), 0)
        self.assertEqual(len(api_test_data.get_request_queue()), 1)

    def test_cancel_unmatched_request(self):
        # given
        request = Request(user_nopark, today(5), today(9), spot_e21.zone)
        api.new_request(request)
        self.assertEqual(len(api_test_data.get_request_queue()), 1)
        # when
        api.cancel_request(request)
        # then
        self.assertEqual(len(api_test_data.get_request_queue()), 0)

    def test_cancel_matched_request(self):
        # given
        original_offer = Offer.unmatched(spot_e21, hours(3, 12))
        api.new_offer(original_offer)
        request = Request(user_nopark, today(5), today(9), spot_e21.zone)
        api.new_request(request)
        self.assertEqual(api_test_data.get_matched_offers(), [Offer.matched_with(spot_e21, request)])
        self.assertEqual(len(api_test_data.get_unmatched_offers()), 2)
        # when
        api.cancel_request(request)
        # then
        self.assertEqual(len(api_test_data.get_matched_offers()), 0)
        self.assertEqual(api_test_data.get_unmatched_offers(), [original_offer])

    def test_cancel_request_new_takes_over(self):
        # given
        api.new_offer(Offer.unmatched(spot_e11, hours(3, 12)))
        first_request = Request(user_nopark, today(5), today(10), spot_e11.zone)
        api.new_request(first_request)
        second_request = Request(user_oute2, today(6), today(12), spot_e11.zone)
        api.new_request(second_request)
        self.assertEqual(api_test_data.get_matched_offers(), [Offer.matched_with(spot_e11, first_request)])
        self.assertEqual(api_test_data.get_request_queue(), [second_request])
        # when
        api.cancel_request(first_request)
        # then
        self.assertEqual(api_test_data.get_matched_offers(), [Offer.matched_with(spot_e11, second_request)])
        self.assertEqual(len(api_test_data.get_request_queue()), 0)


if __name__ == '__main__':
    unittest.main()

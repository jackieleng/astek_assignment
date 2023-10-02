import unittest
from unittest.mock import MagicMock
from math import factorial

from raffle import TICKET_PRICE, Raffle, State, INITIAL_POT_SIZE, generate_numbers



class TestRaffle(unittest.TestCase):
    def test_create_raffle(self):
        """Test creating Raffle object will initialize attributes"""
        raffle = Raffle()
        self.assertEqual(State.NOT_STARTED, raffle.state)
        self.assertEqual(INITIAL_POT_SIZE, raffle.pot_size)
        self.assertEqual(dict(), raffle.name2tickets)
        self.assertEqual(0, raffle.reward)
        self.assertTrue(len(raffle.available_tickets) > 0)
        num_combinations = factorial(15) / (factorial(10) * factorial(5))
        self.assertEqual(num_combinations, len(raffle.available_tickets))

    def test_generate_numbers(self):
        self.assertEqual(5, len(generate_numbers()))

    def test_handle_option(self):
        """Test given option 1/2/3 the handlers are called"""
        raffle = Raffle()
        raffle.get_new_state = MagicMock()
        raffle.handle_new_draw = MagicMock()
        raffle.handle_option(1)
        raffle.get_new_state.assert_called_with(1)
        raffle.handle_new_draw.assert_called()

        raffle.handle_buy_tickets = MagicMock()
        raffle.handle_option(2)
        raffle.get_new_state.assert_called_with(2)

        raffle.handle_run_raffle = MagicMock()
        raffle.handle_option(3)
        raffle.get_new_state.assert_called_with(3)

    def test_handle_new_draw_state(self):
        """Test new draw changes the state from NOT_STARTED to ONGOING"""
        raffle = Raffle()
        raffle.handle_new_draw = MagicMock()
        self.assertEqual(raffle.state, State.NOT_STARTED)
        raffle.handle_option(1)
        self.assertEqual(raffle.state, State.ONGOING)

    def test_handle_buy_state(self):
        """Test buy ticket keeps state at ONGOING"""
        raffle = Raffle(state=State.ONGOING)
        raffle.handle_buy_tickets = MagicMock()
        self.assertEqual(raffle.state, State.ONGOING)
        raffle.handle_option(2)
        self.assertEqual(raffle.state, State.ONGOING)

    def test_handle_run_raffle_state(self):
        """Test run raffle changes state from ONGOING to NOT_STARTED"""
        raffle = Raffle(state=State.ONGOING)
        raffle.handle_run_raffle = MagicMock()
        self.assertEqual(raffle.state, State.ONGOING)
        raffle.handle_option(3)
        self.assertEqual(raffle.state, State.NOT_STARTED)


class TestNewDraw(unittest.TestCase):
    def test_handle_new_draw(self):
        """Test calling handle_new_draw() should reset all available/bought tickets to initial state"""
        raffle = Raffle()
        raffle.name2tickets = {'foo': [set([1,2,3,4,5])]}
        raffle.available_tickets = []
        raffle.handle_new_draw()
        self.assertEqual(0, len(raffle.name2tickets))
        self.assertTrue(len(raffle.available_tickets) != 0)


class TestBuyTickets(unittest.TestCase):
    def test_handle_buy_tickets_state_fail(self):
        """Test can't buy ticket if not in ONGOING state"""
        raffle = Raffle(state=State.NOT_STARTED)
        raffle.get_name_and_num_tickets = MagicMock()
        raffle.get_name_and_num_tickets.return_value = 'foo', 3
        with self.assertRaises(ValueError):
            raffle.handle_option(2)

    def test_handle_buy_tickets(self):
        """Test user input and buy_tickets() gets called from handle_buy_tickets()"""
        raffle = Raffle(state=State.ONGOING)
        raffle.get_name_and_num_tickets = MagicMock()
        raffle.get_name_and_num_tickets.return_value = 'foo', 3
        raffle.buy_tickets = MagicMock()
        raffle.handle_buy_tickets()
        raffle.buy_tickets.assert_called_with('foo', 3)

    def test_buy_tickets(self):
        """Test buying tickets should add to pot_size"""
        raffle = Raffle(state=State.ONGOING, pot_size=0)
        # buying 5+4=9 tickets for foo and bar
        raffle.buy_tickets('foo', 5)
        self.assertTrue('foo' in raffle.name2tickets)
        self.assertEqual(5 * TICKET_PRICE, raffle.pot_size)
        raffle.buy_tickets('bar', 4)
        self.assertTrue('bar' in raffle.name2tickets)
        self.assertEqual(9 * TICKET_PRICE, raffle.pot_size)

    def test_no_more_tickets(self):
        """Test you can't buy more than the available number of tickets"""
        raffle = Raffle(state=State.ONGOING, pot_size=0)
        num_tickets = len(raffle.available_tickets) + 999
        raffle.buy_tickets('foo', num_tickets)
        self.assertTrue(0 < len(raffle.name2tickets['foo']) < num_tickets)

    def test_buy_tickets_reduces_available_tickets(self):
        """Test buying tickets should remove them from the available tickets"""
        raffle = Raffle(state=State.ONGOING, pot_size=0)
        len_before = len(raffle.available_tickets)
        raffle.buy_tickets('foo', 3)
        tickets = raffle.name2tickets['foo']
        self.assertEqual(len_before - 3, len(raffle.available_tickets))
        for ticket in tickets:
            self.assertTrue(ticket not in raffle.available_tickets)


class TestRunRaffle(unittest.TestCase):
    def test_handle_run_raffle_state_fail(self):
        """Test can't run raffle if not in ONGOING state"""
        raffle = Raffle(state=State.NOT_STARTED)
        with self.assertRaises(ValueError):
            raffle.handle_option(3)

    def test_handle_run_raffle_reward(self):
        """Test that reward value gets updated when hande_run_raffle() is called"""
        raffle = Raffle(state=State.ONGOING)
        raffle.decr_reward_from_pot = MagicMock()
        raffle.get_groups = MagicMock()
        raffle.get_groups.return_value = {
            2: ['placeholder'],
        }

        reward_before = raffle.reward
        raffle.aggregate_winners = MagicMock()
        raffle.aggregate_winners.return_value = {
            'foo': 1,
            'bar': 1,
        }
        raffle.calc_payout_per_user = MagicMock()
        raffle.calc_payout_per_user.return_value = {
            'foo': 10,
            'bar': 20,
        }
        raffle.handle_run_raffle()
        self.assertEqual(reward_before + 30, raffle.reward)

    def test_handle_run_raffle_pot_size(self):
        """Test rewarded amount gets subtracted from pot_size"""
        raffle = Raffle(state=State.ONGOING)
        pot_size_before = raffle.pot_size
        raffle.handle_run_raffle()
        self.assertEqual(pot_size_before, raffle.pot_size)

        raffle = Raffle(state=State.ONGOING)
        raffle.reward = 10
        pot_size_before = raffle.pot_size
        raffle.handle_run_raffle()
        self.assertEqual(pot_size_before - 10, raffle.pot_size)
        self.assertEqual(0, raffle.reward)

    def test_handle_run_raffle(self):
        """Test handle_run_raffle() subtracts the correct percentages from pot based on number of winning numbers"""
        name2tickets = {
            'two': [
                set([1,2,6,7,8])
            ],
            'three': [
                set([4,5,3,8,9])
            ],
            'five': [
                set([1,2,3,4,5])
            ],
        }
        raffle = Raffle(
            state=State.ONGOING,
            name2tickets=name2tickets,
        )
        raffle.get_winning_ticket = MagicMock()
        raffle.get_winning_ticket.return_value = set([1,2,3,4,5])
        pot_before = raffle.pot_size
        raffle.handle_run_raffle()
        self.assertEqual(pot_before - .1*pot_before - .15*pot_before - .5*pot_before, raffle.pot_size)

    def test_handle_run_raffle_2(self):
        """Test handle_run_raffle() subtracts the correct percentages from pot based on number of winning numbers"""
        name2tickets = {
            'two': [
                set([1,2,6,7,8]),
            ],
            'three_and_two': [
                set([3,4,5,8,9]),
                set([3,4,8,9,10]),
            ],
        }
        raffle = Raffle(
            state=State.ONGOING,
            name2tickets=name2tickets,
        )
        raffle.get_winning_ticket = MagicMock()
        raffle.get_winning_ticket.return_value = set([1,2,3,4,5])
        pot_before = raffle.pot_size
        raffle.handle_run_raffle()
        self.assertEqual(pot_before - .1*pot_before - .15*pot_before, raffle.pot_size)

    def test_handle_run_raffle_README(self):
        """Test using the example from the README.md"""
        name2tickets = {
            'James': [
                set([4,7,8,13,14]),
            ],
            'Ben': [
                set([3,6,9,11,13]),
                set([3,7,8,11,14]),
            ],
            'Romeo': [
                set([3,7,9,14,15]),
                set([4,5,10,12,15]),
                set([1,2,7,12,13]),
            ],
        }
        raffle = Raffle(
            state=State.ONGOING,
            name2tickets=name2tickets,
            pot_size=100+6*TICKET_PRICE,
        )
        raffle.get_winning_ticket = MagicMock()
        raffle.get_winning_ticket.return_value = set([3,7,8,11,12])
        raffle.handle_run_raffle()

        res = raffle.draw_results
        self.assertEqual(3, len(res[2]))
        self.assertIn({'name': 'James', 'count': 1, 'payout': 3.25}, res[2])
        self.assertIn({'name': 'Ben', 'count': 1, 'payout': 3.25}, res[2])
        self.assertIn({'name': 'Romeo', 'count': 2, 'payout': 6.5}, res[2])
        self.assertEqual(0, len(res[3]))
        self.assertEqual(1, len(res[4]))
        self.assertIn({'name': 'Ben', 'count': 1, 'payout': 32.5}, res[4])
        self.assertEqual(0, len(res[5]))

        self.assertEqual(100+6*TICKET_PRICE-3.25*2-6.5-32.5, raffle.pot_size)
            

    def test_get_groups(self):
        """Test get_groups() groups tickets correcty based on number of winning numbers"""
        name2tickets = {
            'two': [
                set([1,2,6,7,8]),
            ],
            'three_and_two': [
                set([3,4,5,8,9]),
                set([3,4,8,9,10]),
            ],
            'five': [
                set([1,2,3,4,5])
            ],
        }
        raffle = Raffle(
            state=State.ONGOING,
            name2tickets=name2tickets,
        )
        groups = raffle.get_groups(raffle.name2tickets, set([1,2,3,4,5]))
        self.assertEqual(2, len(groups[2]))
        self.assertEqual(1, len(groups[3]))
        self.assertEqual(0, len(groups[4]))
        self.assertEqual(1, len(groups[5]))

    def test_calc_payout(self):
        """Test user payout calculation"""
        raffle = Raffle(state=State.ONGOING)
        user2count = {
            'foo': 1,
            'bar': 1,
        }
        name2payout = raffle.calc_payout_per_user(user2count, 10)
        self.assertEqual(name2payout['foo'], 5)
        self.assertEqual(name2payout['bar'], 5)

        raffle = Raffle(state=State.ONGOING)
        user2count = {
            'foo': 3,
            'bar': 3,
        }
        name2payout = raffle.calc_payout_per_user(user2count, 10)
        self.assertEqual(name2payout['foo'], 5)
        self.assertEqual(name2payout['bar'], 5)

    def test_calc_payout_2(self):
        """Test user payout calculation"""
        raffle = Raffle(state=State.ONGOING)
        user2count = {
            'foo': 1,
            'bar': 2,
            'baz': 2
        }
        name2payout = raffle.calc_payout_per_user(user2count, 10)
        self.assertEqual(name2payout['foo'], 2)
        self.assertEqual(name2payout['bar'], 4)
        self.assertEqual(name2payout['baz'], 4)



if __name__ == '__main__':
    unittest.main()

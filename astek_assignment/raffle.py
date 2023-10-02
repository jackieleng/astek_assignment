from typing import Optional, Set, Dict, List, Tuple
from enum import Enum, auto
import itertools
import random


INITIAL_POT_SIZE = 100
TICKET_PRICE = 5


class State(Enum):
    NOT_STARTED = auto()
    ONGOING = auto()


def get_welcome(state: State, pot_size: Optional[int] = None) -> str:
    if state == State.NOT_STARTED:
        return (
            "Welcome to My Raffle App"
            "\nStatus: Draw has not started"
        )
    elif state == State.ONGOING:
        return (
            f"Welcome to My Raffle App"
            f"\nStatus: Draw is ongoing. Raffle pot size is ${pot_size}" 
        )
    raise ValueError(f"Invalid state {state}")


def get_option() -> int:
    options = (
        "\n[1] Start a New Draw"
        "\n[2] Buy Tickets"
        "\n[3] Run Raffle\n"
    )
    selected = input(options)
    if selected not in {'1', '2', '3'}:
        raise ValueError(f"Invalid option: {selected}")
    return int(selected)


def press_any_key():
    input("Press any key to return to main menu")


def generate_numbers() -> Set:
    """Generate 5 random numbers between 1-15"""
    return set(random.sample(range(1, 16), 5))


def generate_available_tickets():
    """Generate all number combinations for the tickets"""
    return list(itertools.combinations(range(1, 16), 5))


def fmt_ticket(ticket: Set) -> str:
    return " ".join(str(x) for x in ticket)


class Raffle:
    def __init__(
        self,
        state: Optional[State] = None,
        pot_size: Optional[int] = None,
        name2tickets: Optional[Dict] = None,
        available_tickets: Optional[List] = None,
    ) -> None:
        self.state = State.NOT_STARTED if state is None else state
        self.pot_size = INITIAL_POT_SIZE if pot_size is None else pot_size
        self.name2tickets = dict() if name2tickets is None else name2tickets
        self.available_tickets = (
            generate_available_tickets() if available_tickets is None else available_tickets
        )
        self.reward = 0
        self.draw_results = dict()

    def update_pot_size(self, val: int = 0) -> int:
        self.pot_size += val
        return self.pot_size

    def get_new_state(self, option: int) -> State:
        """Get new state based on selected option"""
        transitions = {
            1: {State.NOT_STARTED: State.ONGOING},
            2: {State.ONGOING: State.ONGOING},
            3: {State.ONGOING: State.NOT_STARTED},
        }
        old2new = transitions[option]
        try:
            return old2new[self.state]
        except KeyError:
            raise ValueError(f"Invalid state transition (option={option}, old_state={self.state})")

    def reset_available_tickets(self):
        self.available_tickets = generate_available_tickets()

    def get_ticket(self) -> Set:
        """Get a random new ticket from available tickets"""
        if len(self.available_tickets) == 0:
            raise RuntimeError("No more available tickets!")
        i = random.randrange(0, len(self.available_tickets))
        return set(self.available_tickets.pop(i))

    def get_name_and_num_tickets(self) -> Tuple[str, int]:
        rawstr = input("Enter your name, number of tickets to purchase (for e.g. a valid input will be James,1)\n")
        try:
            name, num_tickets = rawstr.split(',')
            num_tickets = int(num_tickets)
            assert len(name) > 0
            assert num_tickets > 0
        except Exception:
            raise ValueError(f"Invalid input: {rawstr}")
        return name, num_tickets


    def buy_tickets(self, name: str, num_tickets: int):
        if name in self.name2tickets:
            raise ValueError(f"Invalid input: {name} has purchased tickets already")
        tickets = []
        no_more_tickets = False
        try:
            for _ in range(num_tickets):
                tickets.append(self.get_ticket())
        except RuntimeError:
            no_more_tickets = True
        self.name2tickets[name] = tickets
        print(f"Hi {name}, you have purchased {len(tickets)} ticket(s)")
        for i, ticket in enumerate(tickets):
            print(f"Ticket {i+1}: {fmt_ticket(ticket)}")
        if no_more_tickets:
            print("No more available tickets!")
        self.update_pot_size(len(tickets) * TICKET_PRICE)

    def handle_buy_tickets(self):
        name, num_tickets = self.get_name_and_num_tickets()
        self.buy_tickets(name, num_tickets)

    def get_groups(self, name2tickets: Dict, winning_ticket: Set) -> Dict[int, List[Tuple[str, Set]]]:
        """Mapping from number of winning numbers to a list of tuples of (name, ticket)"""
        groups = {
            2: [],
            3: [],
            4: [],
            5: [],
        }
        for name, tickets in name2tickets.items():
            for ticket in tickets:
                num_winning_numbers = len(winning_ticket.intersection(ticket))
                if num_winning_numbers in groups:
                    groups[num_winning_numbers].append((name, ticket))
        return groups

    def aggregate_winners(self, name_ticket_tuples: List[Tuple[str, Set]]) -> Dict[str, int]:
        """Aggregate counts"""
        ticket_counts = dict()
        for name, _ in name_ticket_tuples:
            if name not in ticket_counts:
                ticket_counts[name] = 0
            ticket_counts[name] += 1
        return ticket_counts

    def calc_payout_per_user(self, user2count: Dict[str, int], reward: float) -> Dict[str, float]:
        """Calculate payout per user"""
        total_count = sum(user2count.values())
        
        return {
            name: reward * count/total_count
            for name, count
            in user2count.items()
        }

    def decr_reward_from_pot(self):
        """Remove awarded money from pot and zero reward"""
        self.update_pot_size(self.reward * -1)
        self.reward = 0

    def get_winning_ticket(self) -> Set:
        return generate_numbers()

    def get_group_results(self, groups: Dict[int, List[Tuple[str, Set]]]) -> Tuple[Dict[int, List[Dict]], float]:
        """Get a tuple of (results, total_reward)

        Results are grouped by number in list of dicts: 
        {
            2: [
                {
                    'name': 'foo',
                    'count': 2,
                    'payout': 5,
                },
                ...
            ],
            ...
        }
        """
        reward_percentages = {
            2: .1,
            3: .15,
            4: .25,
            5: .5,
        }
        total_reward = 0
        results = dict()
        for group_number, name_ticket_tuples in groups.items():
            results[group_number] = []
            group_reward = reward_percentages[group_number] * self.pot_size
            if len(name_ticket_tuples) == 0:
                continue
            name2ticket_count = self.aggregate_winners(name_ticket_tuples)
            name2payout = self.calc_payout_per_user(name2ticket_count, group_reward)
            for name, payout in name2payout.items():
                count = name2ticket_count[name]
                total_reward += payout
                results[group_number].append({
                    'name': name,
                    'count': count,
                    'payout': payout,
                })
        return results, total_reward

    def print_results(self, results: Dict[int, List[Dict]]):
        for group_number in sorted(results.keys()):
            group_results = results[group_number]
            print(f"Group {group_number} Winners:")
            if len(group_results) == 0:
                print("Nil\n")
                continue
            for res in group_results:
                print(f"{res['name']} with {res['count']} winning ticket(s)- ${res['payout']}")
            print()


    def handle_run_raffle(self):
        winning_ticket = self.get_winning_ticket()
        print(
            "Running Raffle...\n"
            f"Winning ticket is {fmt_ticket(winning_ticket)}\n"
        )
        groups = self.get_groups(self.name2tickets, winning_ticket)
        results, reward = self.get_group_results(groups)
        self.reward += reward
        self.draw_results = results  # for testing purposes
        self.print_results(results)
        self.decr_reward_from_pot()

    def reset_user_tickets(self):
        """Reset tickets bought by users"""
        self.name2tickets = dict()

    def handle_new_draw(self):
        self.reset_available_tickets()
        self.reset_user_tickets()
        print(f"New Raffle draw has been started. Initial pot size: ${self.pot_size}")

    def handle_option(self, option: int):
        if option == 1:
            self.state = self.get_new_state(option)
            self.handle_new_draw()
        elif option == 2:
            new_state = self.get_new_state(option)
            self.handle_buy_tickets()
            self.state = new_state
        elif option == 3:
            new_state = self.get_new_state(option)
            self.handle_run_raffle()
            self.state = new_state


def main():
    raffle = Raffle()

    while True:
        print(get_welcome(raffle.state, raffle.pot_size))
        try:
            opt = get_option()
        except ValueError as err:
            print(err)
            press_any_key()
            continue
        try:
            raffle.handle_option(opt)
            press_any_key()
        except Exception as err:
            print(err)
            press_any_key()
            continue



if __name__ == '__main__':
    main()

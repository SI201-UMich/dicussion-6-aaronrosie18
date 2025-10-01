import os
import unittest


class PollReader():
    """
    A class for reading and analyzing polling data.
    """
    def __init__(self, filename):
        """
        The constructor. Opens up the specified file, reads in the data,
        closes the file handler, and sets up the data dictionary that will be
        populated with build_data_dict().
        """
        # base path for this file (OS-agnostic)
        self.base_path = os.path.abspath(os.path.dirname(__file__))

        # join the base path with the passed filename
        self.full_path = os.path.join(self.base_path, filename)

        # open up the file handler
        self.file_obj = open(self.full_path, 'r', encoding='utf-8')

        # read in each line of the file to a list
        self.raw_data = self.file_obj.readlines()

        # close the file hand
        self.file_obj.close()

        # set up the data dict that we will fill in later
        self.data_dict = {
            'month': [],
            'date': [],
            'sample': [],
            'sample type': [],
            'Harris result': [],
            'Trump result': []
        }

    def _to_fraction(self, val_str):
        """
        Convert a numeric string that may be a percentage (e.g., '49.34')
        or a fraction (e.g., '0.4934') to a fraction in [0,1].
        """
        v = float(val_str)
        if v > 1.0:
            v /= 100.0
        return v

    def build_data_dict(self):
        """
        Reads all of the raw data from the CSV and builds a dictionary where
        each key is the name of a column in the CSV, and each value is a list
        containing the data for each row under that column heading.
        """

        # skip header row and iterate through each data row
        for idx, row in enumerate(self.raw_data):
            if idx == 0:
                continue  # skip header
            separated = [x.strip() for x in row.strip().split(',')]
            if len(separated) < 5:
                continue  # skip incomplete rows

            self.data_dict['month'].append(separated[0])
            self.data_dict['date'].append(int(separated[1]))
            # sample column: e.g., '1880 LV' or '820 RV'
            sample_parts = separated[2].split()
            if len(sample_parts) == 2:
                sample_size = int(sample_parts[0])
                sample_type = sample_parts[1] if sample_parts[1] in ['LV', 'RV'] else 'Unknown'
            else:
                sample_size = int(sample_parts[0])
                sample_type = 'Unknown'
            self.data_dict['sample'].append(sample_size)
            self.data_dict['sample type'].append('likely voters' if sample_type == 'LV' else 'registered voters')
            self.data_dict['Harris result'].append(self._to_fraction(separated[3]))
            self.data_dict['Trump result'].append(self._to_fraction(separated[4]))

    def highest_polling_candidate(self):
        """
        Return the candidate with the highest single polling percentage and the value.
        If equal, return 'EVEN' and the percentage.
        """
        harris_results = self.data_dict['Harris result']
        trump_results = self.data_dict['Trump result']

        max_harris = max(harris_results) if harris_results else 0.0
        max_trump = max(trump_results) if trump_results else 0.0

        if max_harris > max_trump:
            return f"Harris {max_harris*100:.1f}%"
        elif max_trump > max_harris:
            return f"Trump {max_trump*100:.1f}%"
        else:
            return f"EVEN {max_harris*100:.1f}%"

    def likely_voter_polling_average(self):
        """
        Calculate the average polling percentage for each candidate among likely voters.

        Returns:
            tuple: (harris_avg_fraction, trump_avg_fraction)
        """
        harris_likely = []
        trump_likely = []
        for i, stype in enumerate(self.data_dict['sample type']):
            if stype.lower() == 'likely voters':
                harris_likely.append(self.data_dict['Harris result'][i])
                trump_likely.append(self.data_dict['Trump result'][i])

        harris_avg = sum(harris_likely) / len(harris_likely) if harris_likely else 0.0
        trump_avg = sum(trump_likely) / len(trump_likely) if trump_likely else 0.0
        return harris_avg, trump_avg

    def polling_history_change(self):
        """
        Calculate the change in polling averages between the earliest and latest polls.

        This method calculates the average result for each candidate in the earliest 30 polls
        and the latest 30 polls, then returns the net change as fractions.

        Returns:
            tuple: (harris_change_fraction, trump_change_fraction)
        """
        # Get earliest 30 and latest 30 polls
        harris = self.data_dict['Harris result']
        trump = self.data_dict['Trump result']
        n = min(30, len(harris), len(trump))

        if n == 0:
            return 0.0, 0.0

        harris_early_avg = sum(harris[:n]) / n
        trump_early_avg = sum(trump[:n]) / n
        harris_late_avg = sum(harris[-n:]) / n
        trump_late_avg = sum(trump[-n:]) / n

        # Get earliest 30 and latest 30 polls
        harris = self.data_dict['Harris result']
        trump = self.data_dict['Trump result']
        n = min(30, len(harris), len(trump))

        if n == 0:
            return 0.0, 0.0

        harris_early_avg = sum(harris[:n]) / n
        trump_early_avg = sum(trump[:n]) / n
        harris_late_avg = sum(harris[-n:]) / n
        trump_late_avg = sum(trump[-n:]) / n

        harris_change = harris_early_avg - harris_late_avg
        trump_change = trump_early_avg - trump_late_avg
        return harris_change, trump_change


class TestPollReader(unittest.TestCase):
    """
    Test cases for the PollReader class.
    """
    def setUp(self):
        self.poll_reader = PollReader('polling_data.csv')
        self.poll_reader.build_data_dict()

    def test_build_data_dict(self):
        self.assertEqual(len(self.poll_reader.data_dict['date']), len(self.poll_reader.data_dict['sample']))
        self.assertTrue(all(isinstance(x, int) for x in self.poll_reader.data_dict['date']))
        self.assertTrue(all(isinstance(x, int) for x in self.poll_reader.data_dict['sample']))
        self.assertTrue(all(isinstance(x, str) for x in self.poll_reader.data_dict['sample type']))
        self.assertTrue(all(isinstance(x, float) for x in self.poll_reader.data_dict['Harris result']))
        self.assertTrue(all(isinstance(x, float) for x in self.poll_reader.data_dict['Trump result']))

    def test_highest_polling_candidate(self):
        result = self.poll_reader.highest_polling_candidate()
        self.assertTrue(isinstance(result, str))
        self.assertTrue("Harris" in result)
        self.assertTrue("57.0%" in result)

    def test_likely_voter_polling_average(self):
        harris_avg, trump_avg = self.poll_reader.likely_voter_polling_average()
        self.assertTrue(isinstance(harris_avg, float))
        self.assertTrue(isinstance(trump_avg, float))
        self.assertTrue(f"{harris_avg:.2%}" == "49.34%")
        self.assertTrue(f"{trump_avg:.2%}" == "46.04%")

    def test_polling_history_change(self):
        harris_change, trump_change = self.poll_reader.polling_history_change()
        self.assertTrue(isinstance(harris_change, float))
        self.assertTrue(isinstance(trump_change, float))
        self.assertTrue(f"{harris_change:+.2%}" == "+1.53%")
        self.assertTrue(f"{trump_change:+.2%}" == "+2.07%")


def main():
    poll_reader = PollReader('polling_data.csv')
    poll_reader.build_data_dict()

    highest_polling = poll_reader.highest_polling_candidate()
    print(f"Highest Polling Candidate: {highest_polling}")

    harris_avg, trump_avg = poll_reader.likely_voter_polling_average()
    print(f"Likely Voter Polling Average:")
    print(f"  Harris: {harris_avg*100:.2f}%")
    print(f"  Trump: {trump_avg*100:.2f}%")

    harris_change, trump_change = poll_reader.polling_history_change()
    print(f"Polling History Change:")
    print(f"  Harris: {harris_change*100:+.2f}%")
    print(f"  Trump: {trump_change*100:+.2f}%")


if __name__ == '__main__':
    # Run the report and then the tests
    try:
        main()
    except Exception:
        # If main() fails due to missing CSV when running tests, don't block tests.
        pass
    unittest.main(verbosity=2)
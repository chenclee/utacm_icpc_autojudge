#include <iostream>
#include <vector>

using namespace std;

int main()
{
	srand(time(0));
	int t;
	cin >> t;

	cout << t << endl;
	while (t-- > 0)
	{
		vector<char> alphabet;
		for (int i = 0; i < 26; ++i)
		{
			alphabet.push_back((char)('a' + i));
		}

		random_shuffle(alphabet.begin(), alphabet.end());

		int lettersToUse = 1 + (rand() % 26);
		int maxGuesses = 0;

		if (lettersToUse != 26)
		{
			maxGuesses = (rand() % (26 - lettersToUse));
		}

		vector<int> toUse;
		for (int i = 0; i < lettersToUse + maxGuesses; ++i)
		{
			toUse.push_back(i);
		}

		random_shuffle(toUse.begin(), toUse.end());

		bool used = false;
		int k = 500 + (rand() % 501);
		cout << k << endl;

		for (int i = 0; i < k; ++i)
		{
			if (!used && i != k - 1 && rand() % 5 == 0)
			{
				cout << "_";
				used = true;
			}
			else
			{
				cout << alphabet[toUse[rand() % lettersToUse]];
				used = false;
			}
		}
		cout << endl;

		for (int i = 0; i < 26; ++i)
		{
			cout << alphabet[i];
		}
		cout << endl;
	}
}
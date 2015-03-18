#include <iostream>
#include <string>
#include <set>

using namespace std;

int main()
{
	int t;
	cin >> t;

	while (t-- > 0)
	{
		int k;
		cin >> k;
		string s;
		set<char> toGuess;

		cin >> s;
		for (int i = 0; i < s.size(); ++i)
		{
			toGuess.insert(s[i]);
		}

		toGuess.erase('_');

		string guesses;
		cin >> guesses;
		int misses = 0;

		for (int i = 0; i < guesses.size() && toGuess.size() > 0; ++i)
		{
			if (toGuess.find(guesses[i]) != toGuess.end())
			{
				toGuess.erase(guesses[i]);
			}
			else
			{
				++misses;
			}
		}

		if (misses == 0)
		{
			cout << "Are they psychic?!" << endl;
		}
		else
		{
			cout << misses << endl;
		}
	}
}

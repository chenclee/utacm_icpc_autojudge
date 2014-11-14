#include <iostream>
#include <cstdlib>
#include <string>

using namespace std;

string randomGen(int n)
{
	string s = "";

	for (int i = 0; i < n; ++i)
	{
		int random = rand() % 26;
		s += (char)('a' + random);
	}

	return s;
}

string valid(int n)
{
	string s = "";
	int random[26];
	fill(random, random + 26, 0);

	for (int i = 0; i < n; ++i)
	{
		++random[(rand() % 26)];
	}

	int index = rand() % 26;
	int count = 0;

	for (int i = 0; i < 26; ++i)
	{
		if (random[i] % 2 == 1)
		{
			--random[i];
			++count;
		}
	}

	random[index] += count;

	for (int i = 0; i < 26; ++i)
	{
		for (int j = 0; j < random[i]; ++j)
		{
			s += (char)('a' + i);
		}
	}


	return s;
}

int main()
{
	srand(time(0));

	int tests;
	cin >> tests;

	cout << tests << endl;

	while (tests-- > 0)
	{
		// int n = 10;  .
		int n = 1 + (rand() % 20);
		cout << n << endl;

		if (rand() % 2)
		{
			cout << valid(n) << endl;
		}
		else
		{
			cout << randomGen(n) << endl;
		}
	}
}
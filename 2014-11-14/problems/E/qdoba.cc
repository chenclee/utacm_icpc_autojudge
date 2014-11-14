#include <iostream>
#include <algorithm>
#include <string>

#define MAX 1000000

bool ways[MAX + 5]; 

using namespace std;

int get(const string& s, int start)
{
	int sum = 0;
	for (int i = start; i < s.size(); ++i)
	{
		if (s[i] == '.')
		{
			return sum;
		}

		sum *= 10;
		sum += s[i] - '0';
	}

	return sum;
}

bool canSolve(int* costs, int n, int money)
{
	for (int i = 0; i < n; ++i)
	{
		ways[costs[i]] = true;
	}

	for (int i = 0; i <= money; ++i)
	{
		if (!ways[i])
		{
			continue;
		}

		for (int j = 0; j < n; ++j)
		{
			if (i + costs[j] <= money)
			{
				ways[i + costs[j]] = true;
			}
		}
	}

	return ways[money];
}

int main()
{
	int tests;
	cin >> tests;

	while (tests-- > 0)
	{
		string moneyString;
		int money;
		int numMeals;

		cin >> numMeals >> moneyString;

		money = get(moneyString, 0) * 100 + get(moneyString, moneyString.find(".") + 1);

		int meals[numMeals];
		string s;

		for (int i = 0; i < numMeals; ++i)
		{
			cin >> s;
			int dot = s.rfind(".");

			meals[i] = get(s, 0) * 100 + get(s, dot + 1);
		}

		if (canSolve(&meals[0], numMeals, money))
		{
			cout << "YES" << endl;
		}
		else
		{
			cout << "NO" << endl;
		}
		
		fill(ways, ways + MAX + 5, false);
	}
}

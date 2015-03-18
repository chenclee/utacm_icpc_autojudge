#include <iostream>
#include <cmath>
#include <vector>
#include <map>

#define MAX_N 1000

using namespace std;

map<int, int> answers;

int primes[MAX_N + 1];

void getPrimes(int n, vector<int>& p)
{
	while (n > 1)
	{
		p.push_back(primes[n]);
		n /= primes[n];
	}
}

int days(int money, int lunch)
{
	cout << money << " " << lunch << endl;
	if (money < lunch)
	{
		return 0;
	}

	if (answers.find(money) != answers.end())
	{
		return answers[money];
	}

	vector<int> p;
	getPrimes(money, p);

	int d = 0;
	for (int i = 0; i < p.size(); ++i)
	{
		int moneyTaken = money / p[i];
		int leftMoney = money - moneyTaken;

		if (leftMoney >= lunch)
		{
			d = max(d, 1 + days(leftMoney - lunch, lunch));
		}
	}

	answers[money] = d;

	return d;
}

int main()
{

	for (int i = 0; i <= MAX_N; ++i)
	{
		primes[i] = i;
	}

	primes[0] = primes[1] = -1;
	for (int i = 2; i <= MAX_N; i += 2)
	{
		primes[i] = 2;
	}

	for (int i = 3; i <= MAX_N; i += 2)
	{
		int step = i + i;
		for (int j = i; j <= MAX_N; j += step)
		{
			primes[j] = min(i, primes[j]);
		}
	}

	int t;
	cin >> t;

	while (t-- > 0)
	{
		int n, l;
		cin >> n >> l;

		cout << days(n, l) << endl;
		answers.clear();
	}
}
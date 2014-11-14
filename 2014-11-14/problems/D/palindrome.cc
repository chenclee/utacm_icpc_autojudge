#include <iostream>
#include <map>
#include <vector>

#define MOD 1000000007

using namespace std;

map<char, int> freq;

long long fact(int n)
{
	long long answer = 1;

	while (n > 1)
	{
		answer *= n;
		answer %= MOD;
		--n;
	}

	return answer;
}

int main()
{
	int tests;
	cin >> tests;

	while (tests-- > 0)
	{
		int n;
		string s;
		cin >> n >> s;

		for (int i = 0; i < s.size(); ++i)
		{
			freq[s[i]] += 1;
		}

		vector<int> pairCounts;
		int sum = 0;
		int odds = 0;

		map<char, int>::iterator it;
		for (it = freq.begin(); it != freq.end(); ++it)
		{
			int frequency = it->second;
			sum += frequency / 2;
			odds += frequency % 2;
			pairCounts.push_back(frequency / 2);
		}

		if (odds >= 2)
		{
			cout << 0 << endl;
		}
		else
		{
			long long numerator = fact(sum);
			long long denominator = 1;

			for (int i = 0; i < pairCounts.size(); ++i)
			{
				denominator *= fact(pairCounts[i]);
				denominator %= MOD;
			}

			cout << numerator / denominator << endl;
		}
		freq.clear();
	}
}

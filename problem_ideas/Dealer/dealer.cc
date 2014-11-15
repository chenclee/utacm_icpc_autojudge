#include <iostream>
#include <algorithm>

#define MAX_SIZE 1000

using namespace std;

int counts[MAX_SIZE];

int main()
{
	int tests;
	cin >> tests;

	while (tests-- > 0)
	{
		int n, k, d;
		cin >> n >> k >> d;

		int cards[n];
		for (int i = 0; i < n; ++i)
		{
			cin >> cards[i];
		}

		for (int i = 0; i < d; ++i)
		{
			counts[i % k] += cards[i];
		}


		fill(counts, counts + MAX_SIZE, 0);
	}
}

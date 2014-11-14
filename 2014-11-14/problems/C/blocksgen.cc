#include <iostream>
#include <cstdlib>
#include <stack>

#define MAX_BLOCKS 1000000

using namespace std;

void swap(int* a, int i, int j)
{
	int temp = a[i];
	a[i] = a[j];
	a[j] = temp;
}

void permute(int* values, int n)
{
	for (int i = 0; i < n; ++i)
	{
		int random = (rand() % (n - i));
		swap(values, random, n - i - 1);
	}
}

void simulate(int* values, int n)
{
	stack<int> s;
	int index = 0;
	int i = 1;

	while (i <= n)
	{
		if (s.empty())
		{
			s.push(i);
			++i;
		}

		if (rand() % 2)
		{
			s.push(i);
			++i;
		}
		else
		{
			values[index++] = s.top();
			s.pop();
		}
	}

	while (!s.empty())
	{
		values[index++] = s.top();
		s.pop();
	}
}

int main()
{
	int tests;
	cin >> tests;
	cout << tests << endl;

	while (tests-- > 0)
	{
		int n = (rand() % MAX_BLOCKS);
		int data[n];

		if (rand() % 2)
		{
			simulate(data, n);
		}
		else
		{
			for (int i = 1; i <= n; ++i)
			{
				data[i - 1] = i;
			}

			permute(data, n);
		}

		cout << n << endl;
		for (int i = 0; i < n; ++i)
		{
			cout << data[i];

			if (i != n - 1)
			{
				cout << " ";
			}
		}
		cout << endl;
	}
}

#include <iostream>
#include <cstdio>

using namespace std;

int main()
{
	srand(time(0));

	int t;
	cin >> t;

	cout << t << endl;

	while (t-- > 0)
	{
		int n = 500 + (rand() % 501);

		cout << n << endl;

		for (int i = 0; i < n; ++i)
		{
			int a = 1 + (rand() % 100);
			int b = 1 + (rand() % 100);

			int op = rand() % 6;

			if (op % 3 == 0)
			{
				if (op / 3 == 0)
				{
					cout << a << " + " << b << " = " << a + b;
				}
				else
				{
					cout << a << " + " << b << " = " << rand() % 100;
				}
			}
			else if (op % 3 == 1)
			{
				if (op / 3 == 0)
				{
					cout << a << " - " << b << " = " << a - b;
				}
				else
				{
					cout << a << " - " << b << " = " << rand() % 100;
				}
			}
			else if (op % 3 == 2)
			{
				if (op / 3 == 0)
				{
					cout << a << " * " << b << " = " << a * b;
				}
				else
				{
					cout << a << " * " << b << " = " << rand() % 100;
				}
			}
			cout << endl;
		}
	}
}
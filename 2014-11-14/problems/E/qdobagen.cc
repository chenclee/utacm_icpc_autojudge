#include <iostream>
#include <cstdlib>

using namespace std;

int main()
{
	srand(time(0));

	int tests;
	cin >> tests;

	cout << tests << endl;

	while (tests-- > 0)
	{
		int dollars = rand() % 10000;
		int pennies = rand() % 100;

		int n = 1 + (rand() % 100);

		cout << dollars << "." << pennies << endl;

		for (int i = 0; i < n; ++i)
		{
			dollars = rand() % 10;
			pennies = rand() % 100;
			cout << dollars << "." << pennies << endl;
		}
	}
}
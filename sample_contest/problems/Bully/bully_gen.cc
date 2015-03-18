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
		int l = max(2, rand() % n);

		cout << n << " " << l << endl;
	}
}
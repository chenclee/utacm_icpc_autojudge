#include <iostream>

using namespace std;

int main()
{
	int tests;
	cin >> tests;

	while (tests-- > 0)
	{
		int n, m, x, y;
		cin >> n >> m >> x >> y;

		if (n * x < m)
		{
			cout << "YES" << endl;
		}
		else
		{
			cout << "NO" << endl;
		}
	}
}

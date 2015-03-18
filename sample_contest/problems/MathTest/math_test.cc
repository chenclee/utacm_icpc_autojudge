#include <iostream>
#include <string>
#include <cstdio>
#include <cmath>

using namespace std;

int main()
{
	int t;
	cin >> t;

	while (t-- > 0)
	{
		int n;
		cin >> n;

		int correct = 0;
		
		int a, b, answer;
		char op, eq;

		for (int i = 0; i < n; ++i)
		{
			cin >> a >> op >> b >> eq >> answer;

			if (op == '+')
			{
				correct += (a + b == answer);
			}
			else if (op == '-')
			{
				correct += (a - b == answer);
			}
			else if (op == '*')
			{
				correct += (a * b == answer);
			}
		}

		float x = 100.0f * correct / n;

		cout << round(x) << "%" << endl;
	}
}

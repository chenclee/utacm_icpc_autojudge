#include <iostream>
#include <vector>
#include <stack>

#define PUSH 0
#define POP 1

using namespace std;

bool success(int* config, int n, vector<int>& ops)
{
	stack<int> blocks;
	int originalIndex = 1;

	for (int i = 0; i < n; ++i)
	{
		int next = config[i];

		while (originalIndex <= next)
		{
			blocks.push(originalIndex);
			ops.push_back(PUSH);
			originalIndex++;
		}

		if (blocks.top() != next)
		{
			return false;
		}

		blocks.pop();
		ops.push_back(POP);
	}

	return true;
}

int main()
{
	int tests;
	cin >> tests;

	while (tests-- > 0)
	{
		int n;
		cin >> n;

		int config[n];
		for (int i = 0; i < n; ++i)
		{
			cin >> config[i];
		}

		vector<int> ops;

		if (success(config, n, ops))
		{
			cout << "YES" << endl;
			for (int i = 0; i < ops.size(); ++i)
			{
				cout << ((ops[i] == POP) ? "PLACE" : "STACK") << endl;
			}
		}
		else
		{
			cout << "NO" << endl;
		}
	}
}

#include <iostream>
#include <string>

#define MAX_SIZE 20

using namespace std;

string keys[MAX_SIZE];

void XOR(string& lock, const string& key)
{
	for (int i = 0; i < lock.size(); ++i)
	{
		lock[i] = (lock[i] == key[i]) ? '0' : '1';
	}
}

bool attempt(int n, int binary, string lock)
{
	int keyIndex = 0;
	while (n-- > 0)
	{
		int bit = binary & 1;

		if (bit)
		{
			XOR(lock, keys[keyIndex]);
		}

		++keyIndex;
		binary >>= 1;
	}

	for (int i = 0; i < lock.size(); ++i)
	{
		if (lock[i] == '1')
		{
			return false;
		}
	}

	return true;
}

bool powerset(int n, string lock)
{
	for (int i = 0; i < (1 << n); ++i)
	{
		if (attempt(n, i, lock))
		{
			return true;
		}
	}

	return false;
}

int main()
{
	int tests;
	cin >> tests;

	while (tests-- > 0)
	{	
		int n, k;
		cin >> n >> k;

		string lock;
		cin >> lock;

		for (int i = 0; i < k; ++i)
		{
			cin >> keys[i];
		}

		if (powerset(n, lock))
		{
			cout << "YES" << endl;
		}
		else
		{
			cout << "NO" << endl;
		}
	}
}
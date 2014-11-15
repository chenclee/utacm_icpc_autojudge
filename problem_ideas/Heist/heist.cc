#include <iostream>
#include <vector>
#include <algorithm>
#include <set>

using namespace std;

struct timeSlot
{
	int start;
	int end;
};

struct item
{
	int timeToTake;
	int value;
};

// Sort by biggest time to left
bool operator<(const timeSlot& a, const timeSlot& b)
{
	return (a.end - a.start + 1) > (b.end - b.start + 1);
}

// Sort by value and then by quickest to take
bool operator<(const item& a, const item& b)
{
	if (a.value != b.value)
	{
		return a.value > b.value;
	}

	return a.timeToTake < b.timeToTake;
}

int main()
{
	int tests;
	cin >> tests;

	while (tests-- > 0)
	{
		int n, k;
		cin >> n >> k;

		vector<timeSlot> times;
		for (int i = 0; i < n; ++i)
		{
			timeSlot ts;
			cin >> ts.start >> ts.end;
			times.push_back(ts);
		}

		vector<item> items;
		for (int i = 0; i < k; ++i)
		{
			item it;
			cin >> it.timeToTake >> it.value;
			items.push_back(it);
		}

		sort(times.begin(), times.end());
		sort(items.begin(), items.end());

		set<int> used;
		int maxValue = 0;
		for (int i = 0; i < k; ++i)
		{
			item& it = items[i];

			for (int j = 0; j < n; ++j)
			{
				if (used.find(j) != used.end())
				{
					continue;
				}

				if (it.timeToTake <= (times[j].end - times[j].start + 1))
				{
					used.insert(j);
					maxValue += it.value;
					break;
				}
			}
		}

		cout << maxValue << endl;
	}
}

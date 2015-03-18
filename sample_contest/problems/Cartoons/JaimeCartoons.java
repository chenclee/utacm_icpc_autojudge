import java.util.*;
import java.io.*;

class State
{
	int channel, index, k;

	public State(int channel, int index, int k)
	{
		this.channel = channel;
		this.index = index;
		this.k = k;
	}

	public boolean equals(Object s)
	{
		if (s instanceof State)
		{
			State s1 = (State) s;

			return this.index == s1.index && this.channel == s1.channel && this.k == s1.k;
		}
	
		return false;
	}

	public int hashCode()
	{
		return 31 * 31 * index + 31 * channel + k;
	}

	public String toString()
	{
		return String.format("(%d, %d, %d)", channel, index, k);
	}
}

public class JaimeCartoons
{
	public static Map<State, Integer> answer = new HashMap<State, Integer>();

	public static void main(String args[])
	{
		Scanner scan = new Scanner(System.in);
		int t = scan.nextInt();

		while (t-- > 0)
		{
			int n = scan.nextInt();
			int c = scan.nextInt();
			int s = scan.nextInt();
			int k = scan.nextInt();

			Set<String> favorites = new HashSet<String>();
			String[][] channels = new String[c][n];

			for (int i = 0; i < s; ++i)
			{
				favorites.add(scan.next());
			}

			for (int i = 0; i < c; ++i)
			{
				for (int j = 0; j < n; ++j)
				{
					channels[i][j] = scan.next();
				}
			}

			int maxChannels = 0;
			for (int i = 0; i < c; ++i)
			{
				maxChannels = Math.max(maxChannels, find(channels, favorites, new State(i, 0, k + ((i == 0) ? 0 : -1))));
			}

			System.out.println(maxChannels);

			answer.clear();
		}
	}

	public static int find(String[][] channels, Set<String> favorites, State s)
	{
		if (s.index >= channels[0].length || s.k < 0)
		{
			return 0;
		}

		if (answer.containsKey(s))
		{
			return answer.get(s);
		}


		int count = (favorites.contains(channels[s.channel][s.index])) ? 1 : 0;

		++s.index;
		
		int maxFound = find(channels, favorites, s);
		
		--s.index;

		if (s.k > 0)
		{
			for (int i = 0; i < channels.length; ++i)
			{
				if (i != s.channel)
				{
					int oldChannel = s.channel;
					s.channel = i;
					++s.index;
					--s.k;

					maxFound = Math.max(maxFound, find(channels, favorites, s));
					
					--s.index;
					++s.k;
					s.channel = oldChannel;
				}
			}
		}

		answer.put(s, count + maxFound);

		return count + maxFound;
	}
}

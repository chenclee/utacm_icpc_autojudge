import java.util.*;
import java.io.*;

public class JaimeMarble
{
	public static void main(String args[]) throws IOException
	{
		Scanner scan = new Scanner(System.in);

		int r = scan.nextInt();
		scan.nextLine();

		while (r-- > 0)
		{
			int p = scan.nextInt();
			scan.nextLine();

			Map<Integer, List<Integer>> tree = new HashMap<Integer, List<Integer>>();

			int[] times = new int[p];

			for (int i = 0; i < p; ++i)
			{
				String[] data = scan.nextLine().split(" ");
				int t = Integer.parseInt(data[0]);

				times[i] = t;

				tree.put(i, new ArrayList<Integer>());

				for (int j = 1; j < data.length; ++j)
				{
					int exit = Integer.parseInt(data[j]);
					tree.get(i).add(exit);
				}
			}

			System.out.println(maxTime(times, tree, 0));
		}
	}

	public static int maxTime(int[] times, Map<Integer, List<Integer>> tree, int node)
	{
		int time = times[node];
		int maxTimeSpent = 0;

		for (Integer i : tree.get(node))
		{
			maxTimeSpent = Math.max(maxTimeSpent, maxTime(times, tree, i));
		}

		return time + maxTimeSpent;
	}

}

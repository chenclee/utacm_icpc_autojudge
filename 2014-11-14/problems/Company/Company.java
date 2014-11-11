import java.io.*;
import java.util.*;

public class Company {
	public static void main(String[] args) throws Exception {
		BufferedReader br = new BufferedReader(new FileReader(new File("input.txt")));
		int TC = Integer.parseInt(br.readLine().trim());
		while (TC-- > 0) {
			StringTokenizer st = new StringTokenizer(br.readLine().trim());
			int N = Integer.parseInt(st.nextToken());
			int S = Integer.parseInt(st.nextToken());
			
			int[] V = new int[N];
			int[] T = new int[N];
			int[] D = new int[N];
			
			for (int i = 0; i < N; i++) {
				st = new StringTokenizer(br.readLine().trim());
				V[i] = Integer.parseInt(st.nextToken());
				T[i] = Integer.parseInt(st.nextToken());
				D[i] = Integer.parseInt(st.nextToken());
			}

			System.out.println("brute force: " + bruteForce(N, S, V, T, D));
			System.out.println("dp: " + dp(N, S, V, T, D));
		}
	}

	// just for testing, too slow to be run on inputs of size > 10
	private static int bruteForce(int N, int S, int[] V, int[] T, int[] D) {
		Set<Integer> set = new TreeSet<Integer>();
		for (int i = 0; i < N; i++) {
			set.add(i);
		}
		
		return helper(0, 0, S, set, V, T, D);
	}

	private static int helper(int curMin, int curValue, int limit, Set<Integer> set, int[] V, int[] T, int[] D) {
		if (set.size() == 0) return curValue;
		
		Set<Integer> iterate = new TreeSet<Integer>(set);
		int max = curValue;
		for (int i : iterate) {
			int timeForTask = T[i] + (curMin/60)*D[i];
			if (curMin + timeForTask <= limit) {
				set.remove(i);
				max = Math.max(max, helper(curMin + timeForTask, curValue + V[i], limit, set, V, T, D));
				set.add(i);
			}
		}
		return max;
	}

	private static int dp(int N, int S, int[] V, int[] T, int[] D) {
		return -1;
	}
}

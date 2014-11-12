import java.io.*;
import java.util.*;

public class Company {
	public static void main(String[] args) throws Exception {
		BufferedReader br = new BufferedReader(new FileReader(new File("input3.txt")));
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
			/*long t = System.currentTimeMillis();
			long max;
			max  = bruteForce(N, S, V, T, D);
			t = System.currentTimeMillis() - t;
			System.out.println("brute force: " + max + ", took " + t + " millis");

			t = System.currentTimeMillis();
			max = dp(N, S, V, T, D);
			t = System.currentTimeMillis() - t;

			System.out.println("dp: " + max + ", took " + t + " millis");*/
			System.out.println(dp(N, S, V, T, D));
		}
	}

	// just for testing, too slow to be run on inputs of size > 10.. O(N!)
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

	// dp solution. O(N*2^N*S)
	// for example, N=15 and S = 10000, N! = ~10^12, O(dp) = 15*2^15*10000 = ~5*10^9
	// with a time limit of 1 minute, on data set 1, my above solution took ~5 minutes, whereas the dp solution took around 5 seconds.
	private static int dp(int N, int S, int[] V, int[] T, int[] D) {
		int pow = 1<<N;
    // dp[current minute][which tasks have been solved] = max value for this state
    int [][] dp = new int[S+1][pow];
    int max = 0;
  
    for (int i = 0; i <= S; i++)
      Arrays.fill(dp[i], Integer.MIN_VALUE);

    dp[0][0] = 0;
  
    for (int t = 0; t <= S; t++) {
      for (int s = 0; s < pow; s++) {
        if (dp[t][s] == Integer.MIN_VALUE) continue;

				//System.out.printf("state in dp[%d][%d] = %d\n", t, s, dp[t][s]);

        for (int i = 0; i < N; i++) {
          if ((s & (1<<i)) == 0) { // haven't done this task yet
            int newTime = t + T[i] + (t/60)*D[i];
            if (newTime <= S) {
              int newState = s | (1<<i);
              dp[newTime][newState] = Math.max(dp[newTime][newState], dp[t][s] + V[i]);
            }
          }
        }

        max = Math.max(max, dp[t][s]);
      }
    }
  
    return max;
	}
}

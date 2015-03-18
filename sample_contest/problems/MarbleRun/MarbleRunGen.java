import java.io.*;
import java.util.*;

public class MarbleRunGen {
	public static void main(String[] args) throws Exception {
		int N = Integer.parseInt(args[0]);
		int E = Integer.parseInt(args[1]);
		
		// bfs
		int[] q = new int[N];
		int w = 1;
		int r = 0;
		List<Integer> remaining = new ArrayList<Integer>();
		for (int i = 1; i < N; i++) remaining.add(i);
		String[] out = new String[N];
		while (r < w) {
			int cur = q[r++];
			int e = 1 + (int)(Math.random()*E);
			if (e > remaining.size()) e = remaining.size();
			String s = ""  + (1 + (int)(Math.random() * 1000));
			while (e-- > 0) {
				int index = (int)(Math.random() * remaining.size());
				int n = remaining.remove(index);
				s += " " + n;
				q[w++] = n;
			}
			out[cur] = s;
		}
		System.out.println(N);
		for (int i = 0; i < N; i++) {
			System.out.println(out[i]);
		}
	}
}

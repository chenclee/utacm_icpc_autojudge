import java.io.*;
import java.util.*;

public class Probe {
	public static void main(String[] args) throws Exception {
		BufferedReader br = new BufferedReader(new FileReader(new File(args[0])));
		int T = Integer.parseInt(br.readLine().trim());
		while (T-- > 0) {
			StringTokenizer st = new StringTokenizer(br.readLine().trim());
			int W = Integer.parseInt(st.nextToken());
			int D = Integer.parseInt(st.nextToken());
			int[] h = new int[W];
			st = new StringTokenizer(br.readLine().trim());
			for (int i = 0; i < W; i++) {
				h[i] = Integer.parseInt(st.nextToken());
			}

			int bestPos = -1;
			int best = Integer.MAX_VALUE;
			int min, max;
			for (int i = 0; i + D <= W; i++) {
				max = min = h[i];
				for (int j = 1; j < D; j++) {
					max = Math.max(max, h[i+j]);
					min = Math.min(min, h[i+j]);
				}
				if (max-min < best) {
					best = max-min;
					bestPos = i;
				}
			}
			System.out.println(bestPos);
		}
	}
}


public class Simulator
{
	public static void main(String[] args) {
		double size = 0;
		double count = 0;
		int iterations = 1000;

		double[] probabilities = {0.5, 0.49};
		for (int i = 0; i < iterations; ++i)
		{
			size += simulate(probabilities);
			++count;
		}

		size /= count;
		System.out.println(size);
	}

	public static int simulate(double[] p)
	{
		int count = 1;
		for (int i = 0; i < p.length; ++i)
		{
			if (Math.random() < p[i])
			{
				count += simulate(p);
			}
		}
		return count;
	}
}
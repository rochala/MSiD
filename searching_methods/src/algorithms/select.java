package algorithms;

import java.util.ArrayList;

public class select extends sorting_algorithm
{
    public select()
    {
        super();
    }

    public select(ArrayList<Integer> source)
    {
        super(source);
    }

    @Override
    public ArrayList<Integer> sort_out()
    {
        for (int i = to_be_sorted.size(); i >= 2; i--)
        {
            int max = max_element_index(i);
            if (max != i - 1)
                swap(i - 1, max);
        }

        return to_be_sorted;
    }

    int max_element_index(int limit)
    {
        int max = 0;
        for (int i = 1; i < limit; i++)
            if (to_be_sorted.get(i) > to_be_sorted.get(max))
                max = i;
        return max;
    }
}

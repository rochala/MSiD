package algorithms;

import java.util.ArrayList;

public class insert extends sorting_algorithm
{
    public insert(ArrayList<Integer> to_be_sorted)
    {
        super(to_be_sorted);
    }

    @Override
    public ArrayList<Integer> sort_out()
    {
        int size = to_be_sorted.size();
        for (int i = 1; i < size; i++)
        {
            int key = to_be_sorted.get(i);
            int j = i - 1;

            while (j >= 0 && to_be_sorted.get(j) > key)
            {
                to_be_sorted.set(j + 1, to_be_sorted.get(j));
                j = j - 1;
            }

            to_be_sorted.set(j + 1, key);
        }

        return to_be_sorted;
    }
}

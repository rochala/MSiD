package algorithms;

import java.util.ArrayList;

public class bubble extends sorting_algorithm
{
    public bubble()
    {
        super();
    }

    public bubble(ArrayList<Integer> source)
    {
        super(source);
    }

    @Override
    public ArrayList<Integer> sort_out()
    {
        int size = to_be_sorted.size();
        for(int i = 0; i < size; i++)
            for(int j = 0; j < size - 1; j++)
                if(to_be_sorted.get(j) > to_be_sorted.get(j + 1))
                    swap(j, j + 1);

        return to_be_sorted;
    }
}

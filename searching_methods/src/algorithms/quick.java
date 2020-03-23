package algorithms;

import java.util.ArrayList;

public class quick extends sorting_algorithm
{
    public quick()
    {
        super();
    }

    public quick(ArrayList<Integer> source)
    {
        super(source);
    }

    @Override
    public ArrayList<Integer> sort_out()
    {
        sorting_procedure(0, to_be_sorted.size() - 1);

        return to_be_sorted;
    }

    void sorting_procedure(int low, int high)
    {
        int pivot = to_be_sorted.get((low + high) / 2);
        int i = low, j = high;

        do{
            while (to_be_sorted.get(i) < pivot) i++;
            while (to_be_sorted.get(j) > pivot) j--;
            if (i <= j)
            {
                swap(i, j);
                i++;
                j--;
            }
        } while (i <= j);

        if (j > low) sorting_procedure(low, j);
        if (i < high) sorting_procedure(i, high);
    }
}

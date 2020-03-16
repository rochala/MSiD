def insertion_sort(list_to_sort):
    for step in range(1, len(list_to_sort)):
        key = list_to_sort[step]
        j = step - 1
        while j >= 0 and list_to_sort[j] > key:
            list_to_sort[j + 1] = list_to_sort[j]
            j -= 1
        list_to_sort[j + 1] = key


def quick_sort(list_to_sort):
    def partition(sub_list, low, hi):
        pivot = sub_list[(low + hi) // 2]
        left = low
        right = hi
        while left <= right:
            while sub_list[left] < pivot:
                left += 1
            while sub_list[right] > pivot:
                right -= 1
            if left <= right:
                sub_list[left], sub_list[right] = sub_list[right], sub_list[left]
                left += 1
                right -= 1
        return left, right

    def quick_sort_fun(list_to_sort, low, hi):
        if low < hi:
            left, right = partition(list_to_sort, low, hi)
            quick_sort_fun(list_to_sort, low, right)
            quick_sort_fun(list_to_sort, left, hi)

    quick_sort_fun(list_to_sort, 0, len(list_to_sort) - 1)


def main():
    list_to_sort = [5, 5, 1, 78, 99, 2, 3, 7]
    print(list_to_sort)
    quick_sort(list_to_sort)
    print(list_to_sort)

    list_to_sort_2 = ["Bob", "Hannah", "Alice", "Peter", "Paul"]
    print(list_to_sort_2)
    insertion_sort(list_to_sort_2)
    print(list_to_sort_2)


if __name__ == "__main__":
    main()

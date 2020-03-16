object SortingMethods extends App {

  def quickSort[T <% Ordered[T]](list: List[T]): List[T] =
    list match {
      case Nil => Nil
      case x :: xs =>
        var (before, after) = xs partition (_ < x)
        quickSort(before) ::: x :: quickSort(after)
    }

  def mergeSort[T <% Ordered[T]](list: List[T]): List[T] = {
    def merge(left: List[T], right: List[T]): List[T] = {
      (left, right) match {
        case (_, Nil) => left
        case (Nil, _) => right
        case (lh :: lt, rh :: rt) =>
          if (lh < rh) lh :: merge(lt, right)
          else rh :: merge(left, rt)
      }
    }
    if (list.length / 2 == 0) list
    else if (list.length < 100) {
      quickSort(list)
    } else {
      val (left, right) = list.splitAt(list.length / 2)
      merge(mergeSort(left), mergeSort(right))
    }
  }
  val r = new scala.util.Random
  println(quickSort(List(6, 1, 125, 76, 14, 5, 1, 1, 6, 1, 6, 8, 8, 5, 3)))
  println(mergeSort(List(6, 1, 125, 76, 14, 5, 1, 1, 6, 1, 6, 8, 8, 5, 3)))
}

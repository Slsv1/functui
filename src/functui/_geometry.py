from typing import NamedTuple, Self

class Coordinate(NamedTuple):
    """An immutable coordinate in 2d space."""
    x: int
    y: int
    def __add__(self, other):
        return Coordinate(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Coordinate(self.x - other.x, self.y - other.y)
    def left(self, by: int):
        return Coordinate(self.x + by, self.y)
    def right(self, by: int):
        return Coordinate(self.x - by, self.y)
    def down(self, by: int):
        return Coordinate(self.x , self.y + by)
    def up(self, by: int):
        return Coordinate(self.x , self.y - by)

class Rect(NamedTuple):
    """A simple immutable rectangle defined by width and height."""

    width: int
    height: int

    def resize(self, width: int = 0, height: int = 0) -> Self:
        """Returns a new Rect resized by expanding or shrinking.

        Positive values expand; negative values shrink.

        Args:
            width: Amount to expand (or shrink) on the x axis.
            height: Amount to expand (or shrink) on the y axis.

        Returns: A new rectangle with altered size.
        """
        return self.__class__(
            width=max(self.width + width, 0),
            height=max(self.height + height, 0),
        )

    def union(self, other: Self) -> Self:
        """Returns a rectangle representing the maximum dimensions of this and another.

        Effectively selects the largest width and height between the two rectangles.
        This method is commutative.

        Args:
            other: The rectangle to compare against.

        Returns:
            Rect: A new rectangle whose dimensions are the max of the two.
        """
        return self.__class__(
            width=self.width if other.width < self.width else other.width,
            height=self.height if other.height < self.height else other.height,
        )

    def clamp(self, other: Self) -> Self:
        """Returns a rectangle clamped so its dimensions do not exceed another rectangle.

        Effectively selects the minimum width and height between the two rectangles.
        This method is commutative.

        Args:
            other: The rectangle whose dimensions act as an upper bound.

        Returns:
            Rect: A new rectangle whose dimensions are the min of the two.
        """
        return self.__class__(
            width=self.width if other.width > self.width else other.width,
            height=self.height if other.height > self.height else other.height,
        )

    def clamp_width(self, width: int) -> Self:
        """Returns a rectangle with its width limited to a maximum value.

        Args:
            width: The maximum allowed width.

        Returns:
            Rect: A new rectangle with width clamped to at most the given value.
        """
        return self.__class__(
            width=self.width if width > self.width else width,
            height=self.height,
        )

    def clamp_height(self, height: int) -> Self:
        """Returns a rectangle with its height limited to a maximum value.

        Args:
            height: The maximum allowed height.

        Returns:
            Rect: A new rectangle with height clamped to at most the given value.
        """
        return self.__class__(
            width=self.width,
            height=self.height if height > self.height else height,
        )

class Box(NamedTuple):
    """An immutable rectangle defined by width, height and position.

    Attributes:
        width: The rectangle's width.
        height: The rectangle's height.
        position: The rectangle's position.
    """
    width: int
    height: int
    position: Coordinate = Coordinate(0, 0)

    @property
    def top(self):
        return self.position.y
    @property
    def bottom(self):
        return self.position.y + self.height
    @property
    def left(self):
        return self.position.x
    @property
    def right(self):
        return self.position.x + self.width

    def resize(
        self,
        top: int = 0,
        bottom: int = 0,
        left: int = 0,
        right: int = 0,
    ) -> Self:
        """Returns a new box resized by expanding or shrinking each side.

        Positive values expand outward; negative values shrink inward.

        Args:
            top: Amount to expand (or shrink) upward. Defaults to 0.
            bottom: Amount to expand downward. Defaults to 0.
            left: Amount to expand leftward. Defaults to 0.
            right: Amount to expand rightward. Defaults to 0.

        Returns:
            A new box with adjusted width, height, and shifted position.
        """
        return self.__class__(
            width=self.width + left + right,
            height=self.height + top + bottom,
            position=self.position - Coordinate(left, top)
        )
    @property
    def rect(self) -> Rect:
        """Returns a Rect representing only this box's size.

        Returns:
            A rectangle with the same width and height as the box.
        """
        return Rect(self.width, self.height)

    def using_rect(self, rect: Rect):
        """Returns a copy of this box but with dimensions replaced by a Rect.

        Args:
            rect: The rectangle whose width and height should be applied.

        Returns:
            A new box with updated width and height, unchanged position.
        """
        return self.__class__(
            height=rect.height,
            width=rect.width,
            position=self.position
        )
    @classmethod
    def from_rect(cls, rect: Rect, position: Coordinate):
        """Create a box with a rect as constructor.

        Args:
            rect: The rectangle whose width and height should be applied.
            position: Box's position.

        Returns:
            A new box with updated width and height, unchanged position.
        """
        return cls(
            height=rect.height,
            width=rect.width,
            position=position
        )
    def is_overlaping(self, other: Self) -> bool:
        """Wrather this box overlaps another box.


        Args:
            other: The box to text overlap with.

        Returns:
            Weather there is an overlap or not.
        """
        return (self.position.x <= other.position.x + other.width and self.position.x + self.width >= other.position.x)\
            and (self.position.y <= other.position.y + other.height and self.position.y + self.height >= other.position.y)

    def intersect(self, other: Self) -> Self:
        """Returns the intersection region between this box and another.

        If the boxes do not overlap, return a new box with width and height set to 0 and same position.

        Args:
            other: The box to intersect with.

        Returns:
            A new box representing the overlap region.
        """
        if not self.is_overlaping(other):
            return self.using_rect(Rect(0, 0))
        x1 = max(self.position.x, other.position.x)
        x2 = min(self.position.x+self.width, other.position.x+other.width)
        y1 = max(self.position.y, other.position.y)
        y2 = min(self.position.y+self.height, other.position.y+other.height)
        return self.__class__(
            height=max(y2-y1, 0),
            width=max(x2-x1, 0),
            position=Coordinate(x1, y1),
        )

    def offset_by(self, coordinate: Coordinate) -> Self:
        """Returns a new box moved by the given coordinate offset.

        Args:
            coordinate: The (dx, dy) offset to apply.

        Returns:
            A new box shifted by the provided coordinate.
        """
        return self.__class__(
            width=self.width,
            height=self.height,
            position=self.position + coordinate
        )

    def union(self, other: Self) -> Self:
        """Returns the smallest box that fully contains both this box and another.

        This method is commutative.

        Args:
            other: The box to union with.

        Returns:
            A new box representing the bounding rectangle of both boxes.
        """
        x1 = min(self.position.x, other.position.x)
        x2 = max(self.position.x+self.width, other.position.x+other.width)
        y1 = min(self.position.y, other.position.y)
        y2 = max(self.position.y+self.height, other.position.y+other.height)
        return self.__class__(
            height=max(y2-y1, 0),
            width=max(x2-x1, 0),
            position=Coordinate(x1, y1),
        )

    def is_point_inside(self, point: Coordinate):
        """Determines whether a point lies within the box's boundaries.

        The check uses half-open bounds: inclusive of the top/left edges,
        exclusive of the bottom/right edges.

        Args:
            point: The point to test.

        Returns:
            True if the point lies inside the box, else False.
        """
        return (self.position.x <= point.x < (self.position.x + self.width))\
            and (self.position.y <= point.y < (self.position.y + self.height)) 

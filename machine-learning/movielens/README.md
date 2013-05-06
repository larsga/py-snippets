
To try this out you first need [the MovieLens example
data](http://www.grouplens.org/node/73).  Specifically, you need the
1M data set.

Once you have done that, either edit ratings.dat to add your own
ratings, or add the following example data to the bottom of it. Note
that the script expects your user ID to be 6041.

    6041::347::4::Bitter Moon
    6041::1680::3::Sliding Doors
    6041::229::5::Death and the Maiden
    6041::1732::3::The Big Lebowski
    6041::597::2::Pretty Woman
    6041::991::4::Michael Collins
    6041::1693::3::Amistad
    6041::1484::4::The Daytrippers
    6041::427::1::Boxing Helena
    6041::509::4::The Piano
    6041::778::5::Trainspotting
    6041::1204::4::Lawrence of Arabia
    6041::1263::5::The Deer Hunter
    6041::1183::5::The English Patient
    6041::1343::1::Cape Fear
    6041::260::1::Star Wars
    6041::405::1::Highlander III
    6041::745::5::A Close Shave
    6041::1148::5::The Wrong Trousers
    6041::1721::1::Titanic

Then simply run:

    python knn-recommend.py

to see recommendation results.
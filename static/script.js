document.addEventListener("DOMContentLoaded", function () {

    console.log("ShopSmart AI loaded successfully!");

    // Button click message
    const buttons = document.querySelectorAll("button");

    buttons.forEach(function (button) {
        button.addEventListener("click", function () {
            console.log("Button clicked:", button.innerText);
        });
    });


    // Home Page Search
    const searchInput = document.getElementById("homeSearchInput");
    const searchButton = document.getElementById("homeSearchButton");

    if (searchInput && searchButton) {

        searchButton.addEventListener("click", function () {

            const searchText = searchInput.value.trim();

            if (searchText !== "") {
                window.location.href =
                    "/search?query=" + encodeURIComponent(searchText);
            }

        });

    }


    // Category Filter + Price Sort
    const categoryFilter = document.getElementById("categoryFilter");
    const priceSort = document.getElementById("priceSort");
    const productList = document.getElementById("product-list");

    if (productList) {

        const productCards =
            Array.from(productList.querySelectorAll(".product-card"));


        function updateProducts() {

            const selectedCategory =
                categoryFilter ? categoryFilter.value : "all";

            const selectedSort =
                priceSort ? priceSort.value : "default";


            // Sort products by price
            if (selectedSort === "lowToHigh") {

                productCards.sort(function (a, b) {

                    const priceA = getPrice(a);
                    const priceB = getPrice(b);

                    return priceA - priceB;

                });

            }


            if (selectedSort === "highToLow") {

                productCards.sort(function (a, b) {

                    const priceA = getPrice(a);
                    const priceB = getPrice(b);

                    return priceB - priceA;

                });

            }


            // Show / Hide based on category
            productCards.forEach(function (card) {

                const categoryText = card
                    .querySelector("p")
                    .innerText
                    .replace("Category: ", "")
                    .trim();


                if (
                    selectedCategory === "all" ||
                    categoryText === selectedCategory
                ) {
                    card.style.display = "block";
                } else {
                    card.style.display = "none";
                }

            });


            // Reorder cards
            productCards.forEach(function (card) {
                productList.appendChild(card);
            });

        }


        function getPrice(card) {

            const paragraphs = card.querySelectorAll("p");

            for (let p of paragraphs) {

                if (p.innerText.startsWith("Price:")) {

                    return Number(
                        p.innerText.replace(/[^\d.]/g, "")
                    );

                }

            }

            return 0;

        }


        // Category change
        if (categoryFilter) {
            categoryFilter.addEventListener("change", updateProducts);
        }


        // Price sort change
        if (priceSort) {
            priceSort.addEventListener("change", updateProducts);
        }

    }

});
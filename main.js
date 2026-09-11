// Nitesh Academy - main.js
"use strict";

const CART_STORAGE_KEY = "niteshAcademyCart";

/* ---------------- MOBILE MENU ---------------- */
function initializeMobileMenu() {
    const menuButton = document.getElementById("mobileMenuButton");
    const navigation = document.getElementById("mainNavigation");

    if (!menuButton || !navigation) return;

    menuButton.addEventListener("click", function () {
        navigation.classList.toggle("active");
        const isOpen = navigation.classList.contains("active");

        menuButton.setAttribute("aria-expanded", String(isOpen));

        const icon = menuButton.querySelector("i");
        if (icon) {
            icon.className = isOpen
                ? "fa-solid fa-xmark"
                : "fa-solid fa-bars";
        }
    });

    navigation.querySelectorAll("a").forEach(function (link) {
        link.addEventListener("click", function () {
            navigation.classList.remove("active");
            menuButton.setAttribute("aria-expanded", "false");

            const icon = menuButton.querySelector("i");
            if (icon) icon.className = "fa-solid fa-bars";
        });
    });
}

/* ---------------- COURSE SELECTION ---------------- */
function initializeCourseSelection() {
    const courseButtons = document.querySelectorAll(".course-menu-button");
    const courseDetails = document.querySelectorAll(".course-detail");

    if (!courseButtons.length || !courseDetails.length) return;

    courseButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const courseId = button.dataset.courseTarget;
            const selectedCourse = document.getElementById(courseId);

            if (!selectedCourse) return;

            courseButtons.forEach(function (item) {
                item.classList.remove("active");
            });

            courseDetails.forEach(function (course) {
                course.classList.remove("active");
            });

            button.classList.add("active");
            selectedCourse.classList.add("active");

            if (window.innerWidth <= 650) {
                selectedCourse.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        });
    });
}

/* ---------------- QUANTITY ---------------- */
function initializeQuantityControls() {
    const quantityButtons = document.querySelectorAll(".quantity-button");

    quantityButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const courseId = button.dataset.courseId;
            const action = button.dataset.action;
            const quantityElement = document.getElementById("qty-" + courseId);

            if (!quantityElement) return;

            let quantity = parseInt(quantityElement.textContent, 10);

            if (isNaN(quantity)) quantity = 1;

            if (action === "increase") quantity++;
            if (action === "decrease" && quantity > 1) quantity--;

            quantityElement.textContent = quantity;
        });
    });
}

/* ---------------- ADD TO CART BUTTON ---------------- */
function initializeAddToCartButtons() {
    const addButtons = document.querySelectorAll(".add-to-cart-button");

    addButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const courseId = String(button.dataset.courseId || "");
            const courseName = String(button.dataset.courseName || "");
            const coursePrice = parseFloat(button.dataset.coursePrice || "0");

            const quantityElement = document.getElementById("qty-" + courseId);
            let quantity = parseInt(quantityElement?.textContent || "1", 10);

            if (isNaN(quantity)) quantity = 1;

            if (!courseId || !courseName || isNaN(coursePrice)) {
                showNotification("Course information is not available.", "error");
                return;
            }

            addCourseToCart({
                id: courseId,
                name: courseName,
                price: coursePrice,
                quantity: quantity
            });

            const oldContent = button.innerHTML;
            button.innerHTML = '<i class="fa-solid fa-check"></i> Added to Cart';
            button.disabled = true;

            setTimeout(function () {
                button.innerHTML = oldContent;
                button.disabled = false;
            }, 1200);
        });
    });
}

/* ---------------- COURSE OPTIONS ---------------- */
function initializeCourseDetailOptions() {
    const cartButton = document.getElementById("courseDetailCartButton");
    const optionInputs = document.querySelectorAll(".course-option-input");
    const finalPriceElement = document.getElementById("courseFinalPrice");

    if (!cartButton) return;

    const basePrice = parseFloat(cartButton.dataset.basePrice || "0") || 0;

    function getSelectedOptions() {
        const selectedOptions = [];
        let optionTotal = 0;

        optionInputs.forEach(function (input) {
            if (input.checked) {
                const option = {
                    id: String(input.value),
                    name: String(input.dataset.name || "Option"),
                    price: parseFloat(input.dataset.price || "0") || 0
                };

                selectedOptions.push(option);
                optionTotal += option.price;
            }
        });

        return {
            selectedOptions: selectedOptions,
            finalPrice: Math.max(0, basePrice + optionTotal)
        };
    }

    function updateFinalPrice() {
        const data = getSelectedOptions();

        if (finalPriceElement) {
            finalPriceElement.textContent =
                data.finalPrice.toLocaleString("en-IN");
        }
    }

    optionInputs.forEach(function (input) {
        input.addEventListener("change", updateFinalPrice);
    });

    cartButton.addEventListener("click", function () {
        const courseId = String(cartButton.dataset.courseId || "");
        const courseName = String(cartButton.dataset.courseName || "Course");
        const quantityElement = document.getElementById("qty-" + courseId);

        let quantity = parseInt(quantityElement?.textContent || "1", 10);
        if (isNaN(quantity)) quantity = 1;

        const selection = getSelectedOptions();
        const selectedOptions = selection.selectedOptions;
        const finalPrice = selection.finalPrice;

        const optionIds = selectedOptions.map(function (option) {
            return option.id;
        }).sort();

        const optionKey = optionIds.join("-") || "standard";

        const optionNames = selectedOptions.map(function (option) {
            return option.name;
        });

        const displayName = optionNames.length
            ? courseName + " (" + optionNames.join(", ") + ")"
            : courseName;

        addCourseToCart({
            id: courseId + ":" + optionKey,
            courseId: courseId,
            name: displayName,
            price: finalPrice,
            quantity: quantity,
            options: optionNames
        });

        const oldContent = cartButton.innerHTML;
        cartButton.innerHTML =
            '<i class="fa-solid fa-check"></i> Package added';
        cartButton.disabled = true;

        setTimeout(function () {
            cartButton.innerHTML = oldContent;
            cartButton.disabled = false;
        }, 900);
    });

    const checkoutButton = document.getElementById("courseDetailCheckoutButton");

    if (checkoutButton) {
        checkoutButton.addEventListener("click", function () {
            cartButton.click();

            setTimeout(function () {
                window.location.href =
                    checkoutButton.dataset.checkoutUrl || "/checkout/";
            }, 150);
        });
    }

    updateFinalPrice();
}

/* ---------------- CART FUNCTIONS ---------------- */
function getCart() {
    try {
        const cartData = localStorage.getItem(CART_STORAGE_KEY);

        if (!cartData) return [];

        const cart = JSON.parse(cartData);
        return Array.isArray(cart) ? cart : [];
    } catch (error) {
        console.error("Unable to read cart:", error);
        return [];
    }
}

function saveCart(cart) {
    try {
        localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart));
    } catch (error) {
        console.error("Unable to save cart:", error);
    }
}

function addCourseToCart(course) {
    const cart = getCart();
    let existingCourse = null;

    for (let i = 0; i < cart.length; i++) {
        if (cart[i].id === course.id) {
            existingCourse = cart[i];
            break;
        }
    }

    if (existingCourse) {
        existingCourse.quantity += course.quantity;
    } else {
        cart.push(course);
    }

    saveCart(cart);
    renderCart();

    showNotification(course.name + " added to your cart.", "success");
}

function initializeCart() {
    renderCart();

    const clearButton = document.getElementById("clearCartButton");
    if (clearButton) {
        clearButton.addEventListener("click", clearCart);
    }

    const checkoutButton = document.getElementById("checkoutButton");
    if (checkoutButton) {
        checkoutButton.addEventListener("click", function (event) {
            if (!getCart().length) {
                event.preventDefault();
                showNotification(
                    "Please add at least one course before checkout.",
                    "error"
                );
            }
        });
    }
}

function renderCart() {
    const cart = getCart();
    const cartContainer = document.getElementById("cartItems");
    const totalAmount = document.getElementById("totalAmount");

    updateHeaderCartCount(cart);

    if (!cartContainer || !totalAmount) return;

    if (!cart.length) {
        cartContainer.innerHTML = `
            <div class="empty-cart">
                <i class="fa-solid fa-basket-shopping"></i>
                <p>Your cart is currently empty.</p>
            </div>
        `;

        totalAmount.textContent = "0.00";
        return;
    }

    let cartHTML = "";

    for (let i = 0; i < cart.length; i++) {
        const item = cart[i];
        const itemTotal = item.price * item.quantity;

        cartHTML += `
            <div class="cart-item">
                <div class="cart-item-name">
                    <strong>${escapeHtml(item.name)}</strong>
                    <small>₹${formatAmount(item.price)} per course</small>
                </div>

                <div class="cart-item-quantity">
                    Quantity: ${item.quantity}
                </div>

                <div class="cart-item-price">
                    ₹${formatAmount(itemTotal)}
                </div>

                <button
                    type="button"
                    class="remove-cart-item"
                    data-remove-course="${escapeHtml(item.id)}"
                    aria-label="Remove ${escapeHtml(item.name)}"
                >
                    <i class="fa-solid fa-trash"></i>
                </button>
            </div>
        `;
    }

    cartContainer.innerHTML = cartHTML;
    totalAmount.textContent = formatAmount(calculateCartTotal(cart));

    cartContainer.querySelectorAll("[data-remove-course]").forEach(function (button) {
        button.addEventListener("click", function () {
            removeCourseFromCart(button.dataset.removeCourse);
        });
    });
}

function removeCourseFromCart(courseId) {
    const cart = getCart();
    const newCart = [];

    for (let i = 0; i < cart.length; i++) {
        if (cart[i].id !== courseId) {
            newCart.push(cart[i]);
        }
    }

    saveCart(newCart);
    renderCart();

    showNotification("Course removed from your cart.", "success");
}

function clearCart() {
    const cart = getCart();

    if (!cart.length) {
        showNotification("Your cart is already empty.", "error");
        return;
    }

    localStorage.removeItem(CART_STORAGE_KEY);
    renderCart();

    showNotification("Your cart has been cleared.", "success");
}

function calculateCartTotal(cart) {
    let total = 0;

    for (let i = 0; i < cart.length; i++) {
        total += cart[i].price * cart[i].quantity;
    }

    return total;
}

function updateHeaderCartCount(cart) {
    if (!cart) cart = getCart();

    const cartCount = document.getElementById("headerCartCount");
    if (!cartCount) return;

    let totalItems = 0;

    for (let i = 0; i < cart.length; i++) {
        totalItems += cart[i].quantity;
    }

    cartCount.textContent = totalItems;
}

function formatAmount(amount) {
    return Number(amount).toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

/* ---------------- CHECKOUT ---------------- */
function initializeCheckoutPage() {
    const checkoutContainer = document.getElementById("checkoutCartItems");
    if (!checkoutContainer) return;

    const subtotalElement = document.getElementById("checkoutSubtotal");
    const totalElement = document.getElementById("checkoutTotal");
    const placeOrderButton = document.getElementById("placeOrderButton");

    function renderCheckout() {
        const cart = getCart();

        if (!cart.length) {
            checkoutContainer.innerHTML = `
                <div class="empty-cart">
                    <i class="fa-solid fa-cart-shopping"></i>
                    <p>No courses found in your cart.</p>
                </div>
            `;

            if (subtotalElement) subtotalElement.textContent = "0.00";
            if (totalElement) totalElement.textContent = "0.00";
            if (placeOrderButton) placeOrderButton.disabled = true;

            return;
        }

        let html = "";

        for (let i = 0; i < cart.length; i++) {
            const item = cart[i];
            const itemTotal = item.price * item.quantity;

            html += `
                <div class="checkout-item">
                    <div>
                        <strong>${escapeHtml(item.name)}</strong>
                        <span>Quantity : ${item.quantity}</span>
                    </div>

                    <div style="display:flex;align-items:center;gap:15px;">
                        <strong>₹${formatAmount(itemTotal)}</strong>

                        <button
                            type="button"
                            class="remove-checkout-item"
                            data-id="${escapeHtml(item.id)}"
                            style="background:#ff3b30;color:#fff;border:none;padding:8px 12px;border-radius:8px;cursor:pointer;"
                        >
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        }

        checkoutContainer.innerHTML = html;

        const total = calculateCartTotal(cart);

        if (subtotalElement) subtotalElement.textContent = formatAmount(total);
        if (totalElement) totalElement.textContent = formatAmount(total);

        document.querySelectorAll(".remove-checkout-item").forEach(function (button) {
            button.addEventListener("click", function () {
                removeCourseFromCart(button.dataset.id);
                renderCheckout();
            });
        });

        if (placeOrderButton) {
            placeOrderButton.disabled = false;

            placeOrderButton.onclick = function () {
                const paymentForm = document.getElementById("checkoutPaymentForm");
                const cartInput = document.getElementById("checkoutCartData");
                const totalInput = document.getElementById("checkoutTotalData");

                if (!paymentForm || !cartInput || !totalInput) {
                    showNotification("Payment form is not available.", "error");
                    return;
                }

                const latestCart = getCart();

                if (!latestCart.length) {
                    showNotification("Your cart is empty.", "error");
                    return;
                }

                cartInput.value = JSON.stringify(latestCart);
                totalInput.value = calculateCartTotal(latestCart);

                paymentForm.submit();
            };
        }
    }

    renderCheckout();
}

/* ---------------- PASSWORD ---------------- */
function initializePasswordToggles() {
    const buttons = document.querySelectorAll(".password-toggle");

    buttons.forEach(function (button) {
        button.addEventListener("click", function () {
            const input = document.getElementById(button.dataset.passwordTarget);
            const icon = button.querySelector("i");

            if (!input) return;

            const showPassword = input.type === "password";

            input.type = showPassword ? "text" : "password";

            if (icon) {
                icon.className = showPassword
                    ? "fa-regular fa-eye-slash"
                    : "fa-regular fa-eye";
            }
        });
    });
}

/* ---------------- HELP SEARCH ---------------- */
function initializeHelpSearch() {
    const searchInput = document.getElementById("helpSearchInput");
    const cards = document.querySelectorAll(".help-card");

    if (!searchInput || !cards.length) return;

    searchInput.addEventListener("input", function () {
        const searchText = searchInput.value.trim().toLowerCase();

        cards.forEach(function (card) {
            const fullText = (
                card.textContent + " " +
                (card.dataset.helpKeywords || "")
            ).toLowerCase();

            const match = !searchText || fullText.includes(searchText);

            card.classList.toggle("hidden", !match);
        });
    });
}

/* ---------------- NOTIFICATION ---------------- */
function showNotification(message, type) {
    if (!type) type = "success";

    const oldNotification = document.querySelector(".site-notification");
    if (oldNotification) oldNotification.remove();

    const notification = document.createElement("div");
    const iconClass = type === "success"
        ? "fa-circle-check"
        : "fa-circle-exclamation";

    notification.className = "site-notification notification-" + type;

    notification.innerHTML = `
        <i class="fa-solid ${iconClass}"></i>
        <span>${escapeHtml(message)}</span>
    `;

    Object.assign(notification.style, {
        position: "fixed",
        right: "20px",
        bottom: "20px",
        zIndex: "9999",
        display: "flex",
        alignItems: "center",
        gap: "10px",
        maxWidth: "380px",
        padding: "14px 18px",
        border: "1px solid rgba(255,255,255,0.16)",
        borderRadius: "14px",
        color: "#ffffff",
        background: type === "success"
            ? "rgba(26, 122, 85, 0.94)"
            : "rgba(158, 45, 61, 0.94)",
        boxShadow: "0 18px 50px rgba(0,0,0,0.35)",
        backdropFilter: "blur(18px)"
    });

    document.body.appendChild(notification);

    setTimeout(function () {
        notification.remove();
    }, 3000);
}

function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = String(value);
    return div.innerHTML;
}

/* ---------------- CAREER QUIZ ---------------- */
function initializeCareerQuiz() {
    const quiz = document.getElementById("careerQuiz");
    if (!quiz) return;

    const answers = {};
    const steps = [...quiz.querySelectorAll(".quiz-step")];
    const result = document.getElementById("quizResult");
    const progress = document.getElementById("quizProgressBar");

    function showStep(number) {
        steps.forEach(function (step) {
            step.classList.toggle(
                "active",
                Number(step.dataset.step) === number
            );
        });

        if (progress) {
            progress.style.width = Math.min(number, 3) * 33.333 + "%";
        }
    }

    quiz.querySelectorAll(".quiz-options button").forEach(function (button) {
        button.addEventListener("click", function () {
            const step = Number(
                button.closest(".quiz-step").dataset.step
            );

            answers[step] = button.dataset.value;

            if (step < 3) {
                showStep(step + 1);
                return;
            }

            steps.forEach(function (item) {
                item.classList.remove("active");
            });

            if (result) result.classList.add("active");
            if (progress) progress.style.width = "100%";

            const goal = answers[1];
            const paceAnswer = answers[3];

            let title;

            if (goal === "frontend") {
                title = "Frontend Experience Path";
            } else if (goal === "backend") {
                title = "Django Backend Path";
            } else {
                title = "Full-Stack Product Builder Path";
            }

            let pace;

            if (paceAnswer === "light") {
                pace = "a flexible 16-week pace";
            } else if (paceAnswer === "intense") {
                pace = "an intensive 8-week sprint";
            } else {
                pace = "a focused 12-week roadmap";
            }

            const titleElement = document.getElementById("quizResultTitle");
            const textElement = document.getElementById("quizResultText");

            if (titleElement) titleElement.textContent = title;

            if (textElement) {
                textElement.textContent =
                    "Based on your goal and experience, start with " +
                    pace +
                    ". Build one portfolio project every milestone.";
            }

            if (result) result.dataset.recommendation = goal;
        });
    });

    document.getElementById("applyRecommendation")?.addEventListener(
        "click",
        function () {
            const recommendation =
                result?.dataset.recommendation || "all";

            let category = "all";

            if (recommendation === "frontend") category = "frontend";
            if (recommendation === "backend") category = "django";

            const search = document.getElementById("courseSearch");

            if (search) {
                search.value = category === "all" ? "" : category;
            }

            filterCourses();

            document.querySelector(".courses-section")?.scrollIntoView({
                behavior: "smooth"
            });
        }
    );

    document.getElementById("resetQuiz")?.addEventListener(
        "click",
        function () {
            if (result) result.classList.remove("active");

            Object.keys(answers).forEach(function (key) {
                delete answers[key];
            });

            showStep(1);
        }
    );

    showStep(1);
}

/* ---------------- COURSE FILTER ---------------- */
let activeCourseCategory = "all";

function initializeCourseDiscovery() {
    const search = document.getElementById("courseSearch");
    const filters = document.querySelectorAll("#categoryFilters button");

    if (!search) return;

    search.addEventListener("input", filterCourses);

    filters.forEach(function (button) {
        button.addEventListener("click", function () {
            filters.forEach(function (item) {
                item.classList.remove("active");
            });

            button.classList.add("active");
            activeCourseCategory = button.dataset.category || "all";

            filterCourses();
        });
    });
}

function filterCourses() {
    const searchInput = document.getElementById("courseSearch");

    const query = (searchInput?.value || "")
        .trim()
        .toLowerCase();

    const buttons = [...document.querySelectorAll(".course-menu-button")];

    let visible = 0;
    let firstVisible = null;

    buttons.forEach(function (button) {
        const name = button.dataset.courseName || "";
        const topics = button.dataset.courseTopics || "";
        const category = button.dataset.courseCategory || "";

        const text = (name + " " + topics + " " + category)
            .toLowerCase();

        const categoryMatch =
            activeCourseCategory === "all" ||
            category === activeCourseCategory;

        const searchMatch =
            !query ||
            text.includes(query);

        const match = categoryMatch && searchMatch;

        button.hidden = !match;

        if (match) {
            visible++;

            if (!firstVisible) {
                firstVisible = button;
            }
        }
    });

    const count = document.getElementById("courseResultCount");

    if (count) count.textContent = visible;

    if (firstVisible) firstVisible.click();
}

/* ---------------- COURSE COMPARE ---------------- */
function initializeCourseCompare() {
    const selectedCourses = new Map();
    const tray = document.getElementById("compareTray");
    const text = document.getElementById("compareTrayText");

    if (!tray || !text) return;

    function updateTray() {
        tray.classList.toggle("active", selectedCourses.size > 0);

        if (!selectedCourses.size) {
            text.textContent = "Select up to 3 courses to compare";
            return;
        }

        const list = [];

        selectedCourses.forEach(function (course) {
            list.push(
                course.name +
                " (" +
                course.duration +
                ", ₹" +
                course.price +
                ")"
            );
        });

        text.textContent = list.join("  •  ");
    }

    const compareButtons = document.querySelectorAll(".compare-button");

    compareButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const id = button.dataset.compareId;

            if (selectedCourses.has(id)) {
                selectedCourses.delete(id);
                button.classList.remove("selected");
            } else if (selectedCourses.size < 3) {
                selectedCourses.set(id, {
                    name: button.dataset.compareName,
                    duration: button.dataset.compareDuration,
                    price: button.dataset.comparePrice
                });

                button.classList.add("selected");
            } else {
                showNotification(
                    "You can compare up to 3 courses.",
                    "error"
                );
            }

            updateTray();
        });
    });

    document.getElementById("clearCompare")?.addEventListener(
        "click",
        function () {
            selectedCourses.clear();

            compareButtons.forEach(function (button) {
                button.classList.remove("selected");
            });

            updateTray();
        }
    );
}

/* ---------------- THEME ---------------- */
function initializeThemeSystem() {
    const root = document.documentElement;
    const toggle = document.getElementById("themeToggle");

    if (!toggle) return;

    function applyTheme(theme, announce) {
        root.dataset.theme = theme;

        const isDark = theme === "dark";

        toggle.setAttribute("aria-pressed", String(isDark));
        toggle.setAttribute(
            "aria-label",
            "Switch to " + (isDark ? "light" : "dark") + " theme"
        );

        toggle.title = isDark ? "Light theme" : "Dark theme";

        try {
            localStorage.setItem("niteshAcademyTheme", theme);
        } catch (error) {}

        if (announce) {
            document.body.classList.add("theme-changing");

            setTimeout(function () {
                document.body.classList.remove("theme-changing");
            }, 520);
        }
    }

    applyTheme(root.dataset.theme || "dark", false);

    toggle.addEventListener("click", function () {
        const newTheme =
            root.dataset.theme === "dark"
                ? "light"
                : "dark";

        applyTheme(newTheme, true);
    });
}

/* ---------------- SCROLL PROGRESS ---------------- */
function initializeScrollProgress() {
    const progress = document.getElementById("scrollProgress");
    if (!progress) return;

    let ticking = false;

    function updateProgress() {
        const maxScroll =
            document.documentElement.scrollHeight - window.innerHeight;

        const percent = maxScroll > 0
            ? Math.min((window.scrollY / maxScroll) * 100, 100)
            : 0;

        progress.style.width = percent + "%";
        ticking = false;
    }

    window.addEventListener(
        "scroll",
        function () {
            if (ticking) return;

            ticking = true;
            requestAnimationFrame(updateProgress);
        },
        { passive: true }
    );

    updateProgress();
}

/* ---------------- ANIMATION SYSTEM ---------------- */
function initializeA1Motion() {
    const reducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    ).matches;

    document.documentElement.classList.add("motion-ready");

    initializeScrollReveal(reducedMotion);
    initializeAnimatedCounters(reducedMotion);

    if (reducedMotion || window.matchMedia("(pointer: coarse)").matches) {
        return;
    }

    initializeSpotlightCards();
    initializeMagneticButtons();
}

function initializeScrollReveal(reducedMotion) {
    const targets = document.querySelectorAll(
        ".section-heading, .glass-card, .glass-panel, .signal-track, .hero-content > *, .course-menu-button, .course-detail"
    );

    targets.forEach(function (element, index) {
        element.classList.add("motion-reveal");

        if (index % 5 === 1) {
            element.classList.add("reveal-left");
        }

        if (index % 5 === 3) {
            element.classList.add("reveal-right");
        }

        element.style.setProperty(
            "--reveal-delay",
            Math.min(index % 5, 4) * 65 + "ms"
        );
    });

    if (reducedMotion || !("IntersectionObserver" in window)) {
        targets.forEach(function (element) {
            element.classList.add("is-visible");
        });

        return;
    }

    const observer = new IntersectionObserver(
        function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;

                entry.target.classList.add("is-visible");
                observer.unobserve(entry.target);
            });
        },
        {
            threshold: 0.12,
            rootMargin: "0px 0px -45px"
        }
    );

    targets.forEach(function (element) {
        observer.observe(element);
    });
}

function initializeSpotlightCards() {
    document.querySelectorAll(".glass-card, .glass-panel").forEach(
        function (card) {
            card.classList.add("spotlight-surface");

            card.addEventListener("pointermove", function (event) {
                const rect = card.getBoundingClientRect();

                const x = event.clientX - rect.left;
                const y = event.clientY - rect.top;

                card.style.setProperty("--spot-x", x + "px");
                card.style.setProperty("--spot-y", y + "px");

                if (
                    !card.matches(
                        ".feature-card, .featured-course-card, .command-center"
                    )
                ) {
                    return;
                }

                const rotateX =
                    ((y / rect.height) - 0.5) * -8;

                const rotateY =
                    ((x / rect.width) - 0.5) * 8;

                card.style.setProperty("--tilt-x", rotateX + "deg");
                card.style.setProperty("--tilt-y", rotateY + "deg");
            });

            card.addEventListener("pointerleave", function () {
                card.style.setProperty("--tilt-x", "0deg");
                card.style.setProperty("--tilt-y", "0deg");
            });
        }
    );
}

function initializeMagneticButtons() {
    document.querySelectorAll(
        ".button, .featured-course-bottom a"
    ).forEach(function (button) {
        button.classList.add("magnetic-action");

        button.addEventListener("pointermove", function (event) {
            const rect = button.getBoundingClientRect();

            const x =
                event.clientX -
                (rect.left + rect.width / 2);

            const y =
                event.clientY -
                (rect.top + rect.height / 2);

            button.style.setProperty(
                "--magnet-x",
                x * 0.16 + "px"
            );

            button.style.setProperty(
                "--magnet-y",
                y * 0.16 + "px"
            );
        });

        button.addEventListener("pointerleave", function () {
            button.style.setProperty("--magnet-x", "0px");
            button.style.setProperty("--magnet-y", "0px");
        });
    });
}

/* ---------------- HERO PARALLAX ---------------- */
function initializeHeroParallax() {
    const hero = document.querySelector(".next-hero");
    const visual = document.querySelector(".command-center");

    if (!hero || !visual) return;

    hero.addEventListener("pointermove", function (event) {
        const rect = hero.getBoundingClientRect();

        const x =
            (event.clientX - rect.left) / rect.width - 0.5;

        const y =
            (event.clientY - rect.top) / rect.height - 0.5;

        visual.style.setProperty("--hero-x", x * 18 + "px");
        visual.style.setProperty("--hero-y", y * 14 + "px");
    });

    hero.addEventListener("pointerleave", function () {
        visual.style.setProperty("--hero-x", "0px");
        visual.style.setProperty("--hero-y", "0px");
    });
}

/* ---------------- CURSOR AURA ---------------- */
function initializeCursorAura() {
    const aura = document.createElement("div");
    aura.className = "cursor-aura";

    document.body.appendChild(aura);

    let targetX = -100;
    let targetY = -100;
    let currentX = -100;
    let currentY = -100;

    window.addEventListener(
        "pointermove",
        function (event) {
            targetX = event.clientX;
            targetY = event.clientY;
            aura.classList.add("active");
        },
        { passive: true }
    );

    function render() {
        currentX += (targetX - currentX) * 0.14;
        currentY += (targetY - currentY) * 0.14;

        aura.style.transform =
            "translate3d(" +
            currentX +
            "px, " +
            currentY +
            "px, 0)";

        requestAnimationFrame(render);
    }

    render();
}

/* ---------------- COUNTERS ---------------- */
function initializeAnimatedCounters(reducedMotion) {
    const counters = document.querySelectorAll(".hero-statistics strong");

    function animate(element) {
        const original = element.textContent.trim();

        const value = parseFloat(
            original.replace(/[^0-9.]/g, "")
        );

        if (!Number.isFinite(value) || reducedMotion) return;

        const suffix = original.replace(/[0-9.]/g, "");
        const start = performance.now();
        const duration = 1100;

        function tick(now) {
            const progress = Math.min(
                (now - start) / duration,
                1
            );

            const eased =
                1 - Math.pow(1 - progress, 3);

            let shown;

            if (Number.isInteger(value)) {
                shown = Math.round(value * eased);
            } else {
                shown = (value * eased).toFixed(1);
            }

            element.textContent = shown + suffix;

            if (progress < 1) {
                requestAnimationFrame(tick);
            }
        }

        requestAnimationFrame(tick);
    }

    if (!("IntersectionObserver" in window)) {
        counters.forEach(animate);
        return;
    }

    const observer = new IntersectionObserver(
        function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;

                animate(entry.target);
                observer.unobserve(entry.target);
            });
        },
        { threshold: 0.7 }
    );

    counters.forEach(function (counter) {
        observer.observe(counter);
    });
}

/* ---------------- PAGE TRANSITIONS ---------------- */
function initializePageTransitionsEarly() {
    const body = document.body;
    const transitionLabel =
        document.getElementById("transitionLabel");

    const reducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    ).matches;

    if (!body) return;

    const path = window.location.pathname;

    let routeValue = 0;

    for (let i = 0; i < path.length; i++) {
        routeValue += path.charCodeAt(i);
    }

    const directions = [
        "transition-direction-side",
        "transition-direction-up",
        "transition-direction-diagonal"
    ];

    body.classList.add(
        directions[routeValue % directions.length]
    );

    function finishEntry() {
        setTimeout(
            function () {
                body.classList.remove("page-entering");
            },
            reducedMotion ? 0 : 380
        );
    }

    if (document.readyState === "complete") {
        finishEntry();
    } else {
        window.addEventListener("load", finishEntry, {
            once: true
        });
    }

    window.addEventListener("pageshow", function (event) {
        if (event.persisted) {
            body.classList.remove("page-leaving");
            body.classList.add("page-entering");
            finishEntry();
        }
    });

    document.addEventListener("click", function (event) {
        const link = event.target.closest("a[href]");

        if (!link || event.defaultPrevented || reducedMotion) return;

        if (
            event.button !== 0 ||
            event.metaKey ||
            event.ctrlKey ||
            event.shiftKey ||
            event.altKey
        ) {
            return;
        }

        if (
            link.target === "_blank" ||
            link.hasAttribute("download")
        ) {
            return;
        }

        const destination =
            new URL(link.href, window.location.href);

        const current =
            new URL(window.location.href);

        const sameDocumentAnchor =
            destination.pathname === current.pathname &&
            destination.search === current.search &&
            destination.hash;

        const unsupportedProtocol =
            !["http:", "https:"].includes(
                destination.protocol
            );

        const external =
            destination.origin !== current.origin;

        if (
            sameDocumentAnchor ||
            unsupportedProtocol ||
            external
        ) {
            return;
        }

        event.preventDefault();

        if (body.classList.contains("page-leaving")) return;

        if (transitionLabel) {
            transitionLabel.textContent =
                "NIT CODERS";
        }

        body.classList.remove("page-entering");
        body.classList.add("page-leaving");

        setTimeout(function () {
            window.location.assign(destination.href);
        }, 220);
    });
}

/* ---------------- START EVERYTHING ---------------- */
document.addEventListener("DOMContentLoaded", function () {
    initializeThemeSystem();
    initializeScrollProgress();
    initializeMobileMenu();
    initializeCourseSelection();
    initializeQuantityControls();
    initializeAddToCartButtons();
    initializeCourseDetailOptions();
    initializeCart();
    initializePasswordToggles();
    initializeHelpSearch();
    initializeCheckoutPage();
    initializeA1Motion();

    initializeCareerQuiz();
    initializeCourseDiscovery();
    initializeCourseCompare();

    initializeHeroParallax();

    if (
        !window.matchMedia("(prefers-reduced-motion: reduce)").matches &&
        !window.matchMedia("(pointer: coarse)").matches
    ) {
        initializeCursorAura();
    }
});

initializePageTransitionsEarly();

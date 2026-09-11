"use strict";

const CART_STORAGE_KEY = "niteshAcademyCart";

document.addEventListener("DOMContentLoaded", () => {
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
});

function initializeMobileMenu() {
    const menuButton = document.getElementById("mobileMenuButton");
    const navigation = document.getElementById("mainNavigation");

    if (!menuButton || !navigation) {
        return;
    }

    menuButton.addEventListener("click", () => {
        const isOpen = navigation.classList.toggle("active");

        menuButton.setAttribute("aria-expanded", String(isOpen));

        const icon = menuButton.querySelector("i");

        if (icon) {
            icon.className = isOpen
                ? "fa-solid fa-xmark"
                : "fa-solid fa-bars";
        }
    });

    navigation.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => {
            navigation.classList.remove("active");
            menuButton.setAttribute("aria-expanded", "false");

            const icon = menuButton.querySelector("i");

            if (icon) {
                icon.className = "fa-solid fa-bars";
            }
        });
    });
}

function initializeCourseSelection() {
    const menuButtons = document.querySelectorAll(".course-menu-button");
    const courseDetails = document.querySelectorAll(".course-detail");

    if (!menuButtons.length || !courseDetails.length) {
        return;
    }

    menuButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const targetId = button.dataset.courseTarget;
            const targetCourse = document.getElementById(targetId);

            if (!targetCourse) {
                return;
            }

            menuButtons.forEach((item) => {
                item.classList.remove("active");
            });

            courseDetails.forEach((course) => {
                course.classList.remove("active");
            });

            button.classList.add("active");
            targetCourse.classList.add("active");

            if (window.innerWidth <= 650) {
                targetCourse.scrollIntoView({
                    behavior: "smooth",
                    block: "start",
                });
            }
        });
    });
}

function initializeQuantityControls() {
    const quantityButtons = document.querySelectorAll(".quantity-button");

    quantityButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const courseId = button.dataset.courseId;
            const action = button.dataset.action;
            const quantityElement = document.getElementById(`qty-${courseId}`);

            if (!quantityElement) {
                return;
            }

            let quantity = Number.parseInt(quantityElement.textContent, 10);

            if (Number.isNaN(quantity)) {
                quantity = 1;
            }

            if (action === "increase") {
                quantity += 1;
            }

            if (action === "decrease" && quantity > 1) {
                quantity -= 1;
            }

            quantityElement.textContent = String(quantity);
        });
    });
}

function initializeAddToCartButtons() {
    const addToCartButtons = document.querySelectorAll(
        ".add-to-cart-button"
    );

    addToCartButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const courseId = String(button.dataset.courseId || "");
            const courseName = String(button.dataset.courseName || "");
            const coursePrice = Number.parseFloat(
                button.dataset.coursePrice || "0"
            );

            const quantityElement = document.getElementById(
                `qty-${courseId}`
            );

            const quantity = Number.parseInt(
                quantityElement?.textContent || "1",
                10
            );

            if (!courseId || !courseName || Number.isNaN(coursePrice)) {
                showNotification(
                    "Course information is not available.",
                    "error"
                );

                return;
            }

            addCourseToCart({
                id: courseId,
                name: courseName,
                price: coursePrice,
                quantity: Number.isNaN(quantity) ? 1 : quantity,
            });

            const originalContent = button.innerHTML;

            button.innerHTML = `
                <i class="fa-solid fa-check"></i>
                Added to Cart
            `;

            button.disabled = true;

            window.setTimeout(() => {
                button.innerHTML = originalContent;
                button.disabled = false;
            }, 1200);
        });
    });
}

function addCourseToCart(course) {
    const cart = getCart();
    const existingCourse = cart.find((item) => item.id === course.id);

    if (existingCourse) {
        existingCourse.quantity += course.quantity;
    } else {
        cart.push(course);
    }

    saveCart(cart);
    renderCart();

    showNotification(
        `${course.name} added to your cart.`,
        "success"
    );
}

function initializeCourseDetailOptions() {
    const cartButton = document.getElementById("courseDetailCartButton");
    const optionInputs = Array.from(document.querySelectorAll(".course-option-input"));
    const finalPriceElement = document.getElementById("courseFinalPrice");

    if (!cartButton) {
        return;
    }

    const basePrice = Number.parseFloat(cartButton.dataset.basePrice || "0");

    const getSelection = () => {
        const selectedOptions = optionInputs
            .filter((input) => input.checked)
            .map((input) => ({
                id: String(input.value),
                name: String(input.dataset.name || "Option"),
                price: Number.parseFloat(input.dataset.price || "0") || 0,
            }));

        const optionTotal = selectedOptions.reduce(
            (total, option) => total + option.price,
            0
        );

        return {
            selectedOptions,
            finalPrice: Math.max(0, basePrice + optionTotal),
        };
    };

    const renderPrice = () => {
        const { finalPrice } = getSelection();

        if (finalPriceElement) {
            finalPriceElement.textContent = finalPrice.toLocaleString("en-IN");
        }
    };

    optionInputs.forEach((input) => {
        input.addEventListener("change", renderPrice);
    });

    cartButton.addEventListener("click", () => {
        const courseId = String(cartButton.dataset.courseId || "");
        const courseName = String(cartButton.dataset.courseName || "Course");
        const quantityElement = document.getElementById(`qty-${courseId}`);
        const quantity = Number.parseInt(quantityElement?.textContent || "1", 10) || 1;
        const { selectedOptions, finalPrice } = getSelection();
        const optionKey = selectedOptions.map((option) => option.id).sort().join("-") || "standard";
        const optionNames = selectedOptions.map((option) => option.name);
        const displayName = optionNames.length
            ? `${courseName} (${optionNames.join(", ")})`
            : courseName;

        addCourseToCart({
            id: `${courseId}:${optionKey}`,
            courseId,
            name: displayName,
            price: finalPrice,
            quantity,
            options: optionNames,
        });

        const originalContent = cartButton.innerHTML;
        cartButton.innerHTML = '<i class="fa-solid fa-check"></i> Package added';
        cartButton.disabled = true;

        window.setTimeout(() => {
            cartButton.innerHTML = originalContent;
            cartButton.disabled = false;
        }, 900);
    });

    const checkoutButton = document.getElementById("courseDetailCheckoutButton");

    if (checkoutButton) {
        checkoutButton.addEventListener("click", () => {
            cartButton.click();
            window.setTimeout(() => {
                window.location.href = checkoutButton.dataset.checkoutUrl || "/checkout/";
            }, 150);
        });
    }

    renderPrice();
}

function getCart() {
    try {
        const storedCart = localStorage.getItem(CART_STORAGE_KEY);

        if (!storedCart) {
            return [];
        }

        const parsedCart = JSON.parse(storedCart);

        return Array.isArray(parsedCart) ? parsedCart : [];
    } catch (error) {
        console.error("Unable to read cart:", error);
        return [];
    }
}

function saveCart(cart) {
    try {
        localStorage.setItem(
            CART_STORAGE_KEY,
            JSON.stringify(cart)
        );
    } catch (error) {
        console.error("Unable to save cart:", error);
    }
}

function initializeCart() {
    renderCart();

    const clearCartButton = document.getElementById("clearCartButton");

    if (clearCartButton) {
        clearCartButton.addEventListener("click", clearCart);
    }

    const checkoutButton = document.getElementById("checkoutButton");

    if (checkoutButton) {
        checkoutButton.addEventListener("click", (event) => {
            const cart = getCart();

            if (!cart.length) {
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
    const cartItemsContainer = document.getElementById("cartItems");
    const totalAmountElement = document.getElementById("totalAmount");

    updateHeaderCartCount(cart);

    if (!cartItemsContainer || !totalAmountElement) {
        return;
    }

    if (!cart.length) {
        cartItemsContainer.innerHTML = `
            <div class="empty-cart">
                <i class="fa-solid fa-basket-shopping"></i>
                <p>Your cart is currently empty.</p>
            </div>
        `;

        totalAmountElement.textContent = "0.00";
        return;
    }

    cartItemsContainer.innerHTML = cart
        .map((item) => {
            const itemTotal = item.price * item.quantity;

            return `
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
        })
        .join("");

    totalAmountElement.textContent = formatAmount(calculateCartTotal(cart));

    cartItemsContainer
        .querySelectorAll("[data-remove-course]")
        .forEach((button) => {
            button.addEventListener("click", () => {
                removeCourseFromCart(button.dataset.removeCourse);
            });
        });
}

function removeCourseFromCart(courseId) {
    const cart = getCart().filter((item) => item.id !== courseId);

    saveCart(cart);
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
    return cart.reduce((total, item) => {
        return total + item.price * item.quantity;
    }, 0);
}

function updateHeaderCartCount(cart = getCart()) {
    const cartCountElement = document.getElementById("headerCartCount");

    if (!cartCountElement) {
        return;
    }

    const count = cart.reduce((total, item) => {
        return total + item.quantity;
    }, 0);

    cartCountElement.textContent = String(count);
}

function formatAmount(amount) {
    return Number(amount).toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
}

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

        checkoutContainer.innerHTML = cart.map(item => {

            const itemTotal = item.price * item.quantity;

            return `
                <div class="checkout-item">

                    <div>
                        <strong>${escapeHtml(item.name)}</strong>
                        <span>Quantity : ${item.quantity}</span>
                    </div>

                    <div style="display:flex;align-items:center;gap:15px;">

                        <strong>₹${formatAmount(itemTotal)}</strong>

                        <button
                            class="remove-checkout-item"
                            data-id="${item.id}"
                            style="
                                background:#ff3b30;
                                color:#fff;
                                border:none;
                                padding:8px 12px;
                                border-radius:8px;
                                cursor:pointer;
                            ">
                            <i class="fa-solid fa-trash"></i>
                        </button>

                    </div>

                </div>
            `;

        }).join("");

        const total = calculateCartTotal(cart);

        subtotalElement.textContent = formatAmount(total);
        totalElement.textContent = formatAmount(total);

        document.querySelectorAll(".remove-checkout-item").forEach(btn => {

            btn.addEventListener("click", () => {

                removeCourseFromCart(btn.dataset.id);

                renderCheckout();

            });

        });

        if (placeOrderButton) {

            placeOrderButton.onclick = function () {

                const paymentForm = document.getElementById("checkoutPaymentForm");
                const cartInput = document.getElementById("checkoutCartData");
                const totalInput = document.getElementById("checkoutTotalData");

                cartInput.value = JSON.stringify(getCart());
                totalInput.value = calculateCartTotal(getCart());

                paymentForm.submit();

            };

        }

    }

    renderCheckout();

}

function initializePasswordToggles() {
    const toggleButtons = document.querySelectorAll(
        ".password-toggle"
    );

    toggleButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const targetId = button.dataset.passwordTarget;
            const input = document.getElementById(targetId);
            const icon = button.querySelector("i");

            if (!input) {
                return;
            }

            const shouldShowPassword = input.type === "password";

            input.type = shouldShowPassword ? "text" : "password";

            if (icon) {
                icon.className = shouldShowPassword
                    ? "fa-regular fa-eye-slash"
                    : "fa-regular fa-eye";
            }
        });
    });
}

function initializeHelpSearch() {
    const input = document.getElementById("helpSearchInput");
    const cards = document.querySelectorAll(".help-card");

    if (!input || !cards.length) {
        return;
    }

    input.addEventListener("input", () => {
        const query = input.value.trim().toLowerCase();

        cards.forEach((card) => {
            const searchableText = `
                ${card.textContent}
                ${card.dataset.helpKeywords || ""}
            `.toLowerCase();

            card.classList.toggle(
                "hidden",
                query !== "" && !searchableText.includes(query)
            );
        });
    });
}

function showNotification(message, type = "success") {
    const previousNotification = document.querySelector(
        ".site-notification"
    );

    if (previousNotification) {
        previousNotification.remove();
    }

    const notification = document.createElement("div");

    notification.className = `site-notification notification-${type}`;

    notification.innerHTML = `
        <i class="fa-solid ${
            type === "success"
                ? "fa-circle-check"
                : "fa-circle-exclamation"
        }"></i>

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
        background:
            type === "success"
                ? "rgba(26, 122, 85, 0.94)"
                : "rgba(158, 45, 61, 0.94)",
        boxShadow: "0 18px 50px rgba(0,0,0,0.35)",
        backdropFilter: "blur(18px)",
    });

    document.body.appendChild(notification);

    window.setTimeout(() => {
        notification.remove();
    }, 3000);
}

function escapeHtml(value) {
    const element = document.createElement("div");
    element.textContent = String(value);
    return element.innerHTML;
}

document.addEventListener("DOMContentLoaded", () => {
    initializeCareerQuiz();
    initializeCourseDiscovery();
    initializeCourseCompare();
});

function initializeCareerQuiz() {
    const quiz = document.getElementById("careerQuiz");
    if (!quiz) return;
    const answers = {};
    const steps = [...quiz.querySelectorAll(".quiz-step")];
    const result = document.getElementById("quizResult");
    const progress = document.getElementById("quizProgressBar");

    const showStep = (number) => {
        steps.forEach((step) => step.classList.toggle("active", Number(step.dataset.step) === number));
        progress.style.width = `${Math.min(number, 3) * 33.333}%`;
    };

    quiz.querySelectorAll(".quiz-options button").forEach((button) => {
        button.addEventListener("click", () => {
            const step = Number(button.closest(".quiz-step").dataset.step);
            answers[step] = button.dataset.value;
            if (step < 3) return showStep(step + 1);

            steps.forEach((item) => item.classList.remove("active"));
            result.classList.add("active");
            progress.style.width = "100%";
            const goal = answers[1];
            const title = goal === "frontend" ? "Frontend Experience Path" : goal === "backend" ? "Django Backend Path" : "Full-Stack Product Builder Path";
            const pace = answers[3] === "light" ? "a flexible 16-week pace" : answers[3] === "intense" ? "an intensive 8-week sprint" : "a focused 12-week roadmap";
            document.getElementById("quizResultTitle").textContent = title;
            document.getElementById("quizResultText").textContent = `Based on your goal and experience, start with ${pace}. Build one portfolio project every milestone.`;
            result.dataset.recommendation = goal;
        });
    });

    document.getElementById("applyRecommendation")?.addEventListener("click", () => {
        const recommendation = result.dataset.recommendation || "all";
        const categoryHint = recommendation === "frontend" ? "frontend" : recommendation === "backend" ? "django" : "all";
        const search = document.getElementById("courseSearch");
        if (search) search.value = categoryHint === "all" ? "" : categoryHint;
        filterCourses();
        document.querySelector(".courses-section")?.scrollIntoView({ behavior: "smooth" });
    });

    document.getElementById("resetQuiz")?.addEventListener("click", () => {
        result.classList.remove("active");
        Object.keys(answers).forEach((key) => delete answers[key]);
        showStep(1);
    });
    showStep(1);
}

let activeCourseCategory = "all";
function initializeCourseDiscovery() {
    const search = document.getElementById("courseSearch");
    const filters = document.querySelectorAll("#categoryFilters button");
    if (!search) return;
    search.addEventListener("input", filterCourses);
    filters.forEach((button) => button.addEventListener("click", () => {
        filters.forEach((item) => item.classList.remove("active"));
        button.classList.add("active");
        activeCourseCategory = button.dataset.category || "all";
        filterCourses();
    }));
}

function filterCourses() {
    const query = (document.getElementById("courseSearch")?.value || "").trim().toLowerCase();
    const buttons = [...document.querySelectorAll(".course-menu-button")];
    let visible = 0;
    buttons.forEach((button) => {
        const haystack = `${button.dataset.courseName || ""} ${button.dataset.courseTopics || ""} ${button.dataset.courseCategory || ""}`;
        const categoryMatch = activeCourseCategory === "all" || button.dataset.courseCategory === activeCourseCategory;
        const match = categoryMatch && (!query || haystack.includes(query));
        button.hidden = !match;
        if (match) visible += 1;
    });
    document.getElementById("courseResultCount").textContent = String(visible);
    const active = buttons.find((button) => !button.hidden);
    if (active) active.click();
}

function initializeCourseCompare() {
    const selected = new Map();
    const tray = document.getElementById("compareTray");
    const text = document.getElementById("compareTrayText");
    if (!tray || !text) return;
    const render = () => {
        tray.classList.toggle("active", selected.size > 0);
        text.textContent = selected.size ? [...selected.values()].map((item) => `${item.name} (${item.duration}, ₹${item.price})`).join("  •  ") : "Select up to 3 courses to compare";
    };
    document.querySelectorAll(".compare-button").forEach((button) => button.addEventListener("click", () => {
        const id = button.dataset.compareId;
        if (selected.has(id)) {
            selected.delete(id); button.classList.remove("selected");
        } else if (selected.size < 3) {
            selected.set(id, { name: button.dataset.compareName, duration: button.dataset.compareDuration, price: button.dataset.comparePrice });
            button.classList.add("selected");
        } else { showNotification("You can compare up to 3 courses.", "error"); }
        render();
    }));
    document.getElementById("clearCompare")?.addEventListener("click", () => {
        selected.clear(); document.querySelectorAll(".compare-button").forEach((button) => button.classList.remove("selected")); render();
    });
}

function initializeThemeSystem() {
    const root = document.documentElement;
    const toggle = document.getElementById("themeToggle");
    if (!toggle) return;

    const applyTheme = (theme, announce = false) => {
        root.dataset.theme = theme;
        const isDark = theme === "dark";
        toggle.setAttribute("aria-pressed", String(isDark));
        toggle.setAttribute("aria-label", `Switch to ${isDark ? "light" : "dark"} theme`);
        toggle.title = `${isDark ? "Light" : "Dark"} theme`;
        try { localStorage.setItem("niteshAcademyTheme", theme); } catch (error) {  }

        if (announce) {
            document.body.classList.add("theme-changing");
            window.setTimeout(() => document.body.classList.remove("theme-changing"), 520);
        }
    };

    applyTheme(root.dataset.theme || "light");
    toggle.addEventListener("click", () => {
        applyTheme(root.dataset.theme === "dark" ? "light" : "dark", true);
    });
}

function initializeScrollProgress() {
    const progress = document.getElementById("scrollProgress");
    if (!progress) return;

    let ticking = false;
    const update = () => {
        const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
        const percent = maxScroll > 0 ? Math.min((window.scrollY / maxScroll) * 100, 100) : 0;
        progress.style.width = `${percent}%`;
        ticking = false;
    };

    window.addEventListener("scroll", () => {
        if (ticking) return;
        ticking = true;
        requestAnimationFrame(update);
    }, { passive: true });
    update();
}

function initializeA1Motion() {
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    document.documentElement.classList.add("motion-ready");

    initializeScrollReveal(reducedMotion);
    initializeAnimatedCounters(reducedMotion);

    if (reducedMotion || window.matchMedia("(pointer: coarse)").matches) return;

    initializeSpotlightCards();
    initializeMagneticButtons();
}

function initializeScrollReveal(reducedMotion) {
    const targets = document.querySelectorAll(
        ".section-heading, .glass-card, .glass-panel, .signal-track, .hero-content > *, .course-menu-button, .course-detail"
    );

    targets.forEach((element, index) => {
        element.classList.add("motion-reveal");
        if (index % 5 === 1) element.classList.add("reveal-left");
        if (index % 5 === 3) element.classList.add("reveal-right");
        element.style.setProperty("--reveal-delay", `${Math.min(index % 5, 4) * 65}ms`);
    });

    if (reducedMotion || !("IntersectionObserver" in window)) {
        targets.forEach((element) => element.classList.add("is-visible"));
        return;
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
        });
    }, { threshold: 0.12, rootMargin: "0px 0px -45px" });

    targets.forEach((element) => observer.observe(element));
}

function initializeSpotlightCards() {
    document.querySelectorAll(".glass-card, .glass-panel").forEach((card) => {
        card.classList.add("spotlight-surface");
        card.addEventListener("pointermove", (event) => {
            const rect = card.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            card.style.setProperty("--spot-x", `${x}px`);
            card.style.setProperty("--spot-y", `${y}px`);

            if (!card.matches(".feature-card, .featured-course-card, .command-center")) return;
            const rotateX = ((y / rect.height) - 0.5) * -8;
            const rotateY = ((x / rect.width) - 0.5) * 8;
            card.style.setProperty("--tilt-x", `${rotateX}deg`);
            card.style.setProperty("--tilt-y", `${rotateY}deg`);
        });
        card.addEventListener("pointerleave", () => {
            card.style.setProperty("--tilt-x", "0deg");
            card.style.setProperty("--tilt-y", "0deg");
        });
    });
}

function initializeMagneticButtons() {
    document.querySelectorAll(".button, .featured-course-bottom a").forEach((button) => {
        button.classList.add("magnetic-action");
        button.addEventListener("pointermove", (event) => {
            const rect = button.getBoundingClientRect();
            const x = event.clientX - (rect.left + rect.width / 2);
            const y = event.clientY - (rect.top + rect.height / 2);
            button.style.setProperty("--magnet-x", `${x * 0.16}px`);
            button.style.setProperty("--magnet-y", `${y * 0.16}px`);
        });
        button.addEventListener("pointerleave", () => {
            button.style.setProperty("--magnet-x", "0px");
            button.style.setProperty("--magnet-y", "0px");
        });
    });
}

function initializeHeroParallax() {
    const hero = document.querySelector(".next-hero");
    const visual = document.querySelector(".command-center");
    if (!hero || !visual) return;

    hero.addEventListener("pointermove", (event) => {
        const rect = hero.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width - 0.5;
        const y = (event.clientY - rect.top) / rect.height - 0.5;
        visual.style.setProperty("--hero-x", `${x * 18}px`);
        visual.style.setProperty("--hero-y", `${y * 14}px`);
    });

    hero.addEventListener("pointerleave", () => {
        visual.style.setProperty("--hero-x", "0px");
        visual.style.setProperty("--hero-y", "0px");
    });
}

function initializeCursorAura() {
    const aura = document.createElement("div");
    aura.className = "cursor-aura";
    document.body.appendChild(aura);

    let targetX = -100, targetY = -100, currentX = -100, currentY = -100;
    window.addEventListener("pointermove", (event) => {
        targetX = event.clientX;
        targetY = event.clientY;
        aura.classList.add("active");
    }, { passive: true });

    const render = () => {
        currentX += (targetX - currentX) * 0.14;
        currentY += (targetY - currentY) * 0.14;
        aura.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
        requestAnimationFrame(render);
    };
    render();
}

function initializeAnimatedCounters(reducedMotion) {
    const counters = document.querySelectorAll(".hero-statistics strong");
    const animate = (element) => {
        const original = element.textContent.trim();
        const value = Number.parseFloat(original.replace(/[^0-9.]/g, ""));
        if (!Number.isFinite(value)) return;
        const suffix = original.replace(/[0-9.]/g, "");
        if (reducedMotion) return;
        const start = performance.now();
        const duration = 1100;
        const tick = (now) => {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            const shown = Number.isInteger(value) ? Math.round(value * eased) : (value * eased).toFixed(1);
            element.textContent = `${shown}${suffix}`;
            if (progress < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
    };

    if (!("IntersectionObserver" in window)) {
        counters.forEach(animate);
        return;
    }
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            animate(entry.target);
            observer.unobserve(entry.target);
        });
    }, { threshold: 0.7 });
    counters.forEach((counter) => observer.observe(counter));
}

(function initializePageTransitionsEarly() {
    const body = document.body;
    const transitionLabel = document.getElementById("transitionLabel");
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (!body) return;

    const routeValue = window.location.pathname
        .split("")
        .reduce((total, character) => total + character.charCodeAt(0), 0);
    const directionClasses = [
        "transition-direction-side",
        "transition-direction-up",
        "transition-direction-diagonal",
    ];
    body.classList.add(directionClasses[routeValue % directionClasses.length]);

    const finishEntry = () => {
        window.setTimeout(() => body.classList.remove("page-entering"), reducedMotion ? 0 : 380);
    };

    if (document.readyState === "complete") finishEntry();
    else window.addEventListener("load", finishEntry, { once: true });

    window.addEventListener("pageshow", (event) => {
        if (event.persisted) {
            body.classList.remove("page-leaving");
            body.classList.add("page-entering");
            finishEntry();
        }
    });

    document.addEventListener("click", (event) => {
        const link = event.target.closest("a[href]");
        if (!link || event.defaultPrevented || reducedMotion) return;
        if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        if (link.target === "_blank" || link.hasAttribute("download")) return;

        const destination = new URL(link.href, window.location.href);
        const current = new URL(window.location.href);
        const isSameDocumentAnchor = destination.pathname === current.pathname &&
            destination.search === current.search && destination.hash;
        const isUnsupportedProtocol = !["http:", "https:"].includes(destination.protocol);
        const isExternal = destination.origin !== current.origin;

        if (isSameDocumentAnchor || isUnsupportedProtocol || isExternal) return;

        event.preventDefault();
        if (body.classList.contains("page-leaving")) return;

        if (transitionLabel) {
            transitionLabel.textContent = "NIT CODERS";
        }

        body.classList.remove("page-entering");
        body.classList.add("page-leaving");
        window.setTimeout(() => window.location.assign(destination.href), 220);
    });
})();

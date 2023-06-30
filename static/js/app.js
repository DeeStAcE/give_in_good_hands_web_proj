document.addEventListener("DOMContentLoaded", function () {
    /**
     * HomePage - Help section
     */
    class Help {
        constructor($el) {
            this.$el = $el;
            this.$buttonsContainer = $el.querySelector(".help--buttons");
            this.$slidesContainers = $el.querySelectorAll(".help--slides");
            this.currentSlide = this.$buttonsContainer.querySelector(".active").parentElement.dataset.id;
            this.paginationLimit = 2;
            this.init();
        }

        init() {
            this.getPagesData()
            this.events();
            this.getPaginationNumbers();
            this.setDisplayedItems(1);
            this.setActivePageButton();
        }

        events() {
            /**
             * Slide buttons
             */
            this.$buttonsContainer.addEventListener("click", e => {
                if (e.target.classList.contains("btn")) {
                    this.changeSlide(e);
                    this.$paginationNumbers.querySelectorAll("li").forEach(e => {
                        this.$paginationNumbers.removeChild(e)
                    })
                    this.getPagesData()
                    this.getPaginationNumbers()
                    this.setDisplayedItems(1);
                    this.setActivePageButton();
                }
            });

            /**
             * Pagination buttons
             */
            this.$el.addEventListener("click", e => {
                if (e.target.classList.contains("btn") && e.target.parentElement.parentElement.classList.contains("help--slides-pagination")) {
                    this.changePage(e);
                }
            });
        }

        changeSlide(e) {
            e.preventDefault();
            const $btn = e.target;

            // Buttons Active class change
            [...this.$buttonsContainer.children].forEach(btn => btn.firstElementChild.classList.remove("active"));
            $btn.classList.add("active");

            // Current slide
            this.currentSlide = $btn.parentElement.dataset.id;

            // Slides active class change
            this.$slidesContainers.forEach(el => {
                el.classList.remove("active");

                if (el.dataset.id === this.currentSlide) {
                    el.classList.add("active");
                }
            });
        }

        // Pagination

        // Get data of the shown elements
        getPagesData() {
            this.$paginatedList = document.querySelector(".help--slides.active");
            this.$paginationNumbers = this.$paginatedList.querySelector("ul.help--slides-pagination");
            this.$listItems = this.$paginatedList.querySelectorAll("ul.help--slides-items li");
            this.currentPage = 1;
            this.pageCount = Math.ceil(this.$listItems.length / this.paginationLimit);
        }

        // Show on page required organizations
        setDisplayedItems(pageNum) {
            this.currentPage = pageNum;

            const prevRange = (pageNum - 1) * this.paginationLimit;
            const currRange = pageNum * this.paginationLimit;

            this.$listItems.forEach((el, index) => {
                el.classList.add("hidden-item")
                if (index >= prevRange && index < currRange) {
                    el.classList.remove("hidden-item")
                }
            })
        }

        // Set class "active" on the right button
        setActivePageButton() {
            this.$paginationNumbers.querySelectorAll("a").forEach(btn => {
                btn.classList.remove("active");

                const pageIndex = btn.getAttribute("page-index")
                if (this.currentPage == pageIndex) {
                    btn.classList.add("active")
                }
            });
        }

        // Get the data of paginated lists
        getPaginationNumbers() {
            for (let i = 1; i <= this.pageCount; i++) {
                const pageNumberLi = document.createElement("li")
                const pageNumberA = document.createElement("a")
                pageNumberA.className = "btn btn--small btn--without-border";
                pageNumberA.innerText = i;
                pageNumberA.setAttribute("page-index", i)
                pageNumberLi.appendChild(pageNumberA)
                this.$paginationNumbers.appendChild(pageNumberLi)
            }
        }

        // Action while clicked page button
        changePage(e) {
            e.preventDefault();
            const $btn = e.target;
            const pageIndex = e.target.getAttribute("page-index");
            this.setDisplayedItems(pageIndex);
            this.setActivePageButton();
        }
    }

    const helpSection = document.querySelector(".help");
    if (helpSection !== null) {
        new Help(helpSection);
    }

    /**
     * Form Select
     */
    class FormSelect {
        constructor($el) {
            this.$el = $el;
            this.options = [...$el.children];
            this.init();
        }

        init() {
            this.createElements();
            this.addEvents();
            this.$el.parentElement.removeChild(this.$el);
        }

        createElements() {
            // Input for value
            this.valueInput = document.createElement("input");
            this.valueInput.type = "text";
            this.valueInput.name = this.$el.name;

            // Dropdown container
            this.dropdown = document.createElement("div");
            this.dropdown.classList.add("dropdown");

            // List container
            this.ul = document.createElement("ul");

            // All list options
            this.options.forEach((el, i) => {
                const li = document.createElement("li");
                li.dataset.value = el.value;
                li.innerText = el.innerText;

                if (i === 0) {
                    // First clickable option
                    this.current = document.createElement("div");
                    this.current.innerText = el.innerText;
                    this.dropdown.appendChild(this.current);
                    this.valueInput.value = el.value;
                    li.classList.add("selected");
                }

                this.ul.appendChild(li);
            });

            this.dropdown.appendChild(this.ul);
            this.dropdown.appendChild(this.valueInput);
            this.$el.parentElement.appendChild(this.dropdown);
        }

        addEvents() {
            this.dropdown.addEventListener("click", e => {
                const target = e.target;
                this.dropdown.classList.toggle("selecting");

                // Save new value only when clicked on li
                if (target.tagName === "LI") {
                    this.valueInput.value = target.dataset.value;
                    this.current.innerText = target.innerText;
                }
            });
        }
    }

    document.querySelectorAll(".form-group--dropdown select").forEach(el => {
        new FormSelect(el);
    });

    /**
     * Hide elements when clicked on document
     */
    document.addEventListener("click", function (e) {
        const target = e.target;
        const tagName = target.tagName;

        if (target.classList.contains("dropdown")) return false;

        if (tagName === "LI" && target.parentElement.parentElement.classList.contains("dropdown")) {
            return false;
        }

        if (tagName === "DIV" && target.parentElement.classList.contains("dropdown")) {
            return false;
        }

        document.querySelectorAll(".form-group--dropdown .dropdown").forEach(el => {
            el.classList.remove("selecting");
        });
    });

    /**
     * Switching between form steps
     */
    class FormSteps {
        constructor(form) {
            this.$form = form;
            this.$next = form.querySelectorAll(".next-step");
            this.$prev = form.querySelectorAll(".prev-step");
            this.$step = form.querySelector(".form--steps-counter span");
            this.currentStep = 1;

            this.$stepInstructions = form.querySelectorAll(".form--steps-instructions p");
            const $stepForms = form.querySelectorAll("form > div");
            this.slides = [...this.$stepInstructions, ...$stepForms];

            this.init();
        }

        /**
         * Init all methods
         */
        init() {
            this.events();
            this.updateForm();
        }

        /**
         * All events that are happening in form
         */
        events() {
            // Next step
            this.$next.forEach(btn => {
                btn.addEventListener("click", e => {
                    e.preventDefault();
                    this.currentStep++;
                    this.updateForm();
                });
            });

            // Previous step
            this.$prev.forEach(btn => {
                btn.addEventListener("click", e => {
                    e.preventDefault();
                    this.currentStep--;
                    this.updateForm();
                });
            });

            // Form submit
            this.$form.querySelector("form").addEventListener("submit", e => this.submit(e));
        }

        /**
         * Update form front-end
         * Show next or previous section etc.
         */
        updateForm() {
            this.$step.innerText = this.currentStep;
            // TODO: Validation

            this.slides.forEach(slide => {
                slide.classList.remove("active");

                if (slide.dataset.step == this.currentStep) {
                    slide.classList.add("active");
                }
            });

            form.querySelector("div[data-step='5'] button[type='submit']").innerText = 'Potwierdzam'

            this.$stepInstructions[0].parentElement.parentElement.hidden = this.currentStep >= 6;
            this.$step.parentElement.hidden = this.currentStep >= 6;

            // get data from inputs and show them in summary
            // Getting data from inputs
            const categories = document.querySelectorAll("input[name='categories']:checked")
            const quantity = document.querySelector("input[name='bags']")
            const organization = document.querySelector("input[name='organization']:checked")
            const organizationName = organization.parentElement.querySelector('div.title').innerText
            const formStep4Inputs = form.querySelectorAll("div[data-step='4'] div.form-group--inline input")
            const textArea = form.querySelector("div[data-step='4'] div.form-group--inline textarea")

            // filtering organizations by entered categories
            const organizations = document.querySelectorAll("#organization-choice div.form-group--checkbox")
            organizations.forEach(e => {
                categories.forEach(cat => {
                    if (!e.querySelector('#categories-inst').innerText.includes(cat.value)) {
                        e.style.display = 'none';
                    }
                })
            });

            // show data in the summary
            const summaryItems = form.querySelectorAll("div[data-step='5'] span.summary--text")
            const listElements = form.querySelectorAll("div[data-step='5'] div.form-section--column li")

            summaryItems[0].innerText = `${quantity.value} x 60l worków z przedmiotami`
            summaryItems[1].innerText = `${organizationName}`

            for (let i = 0; i < formStep4Inputs.length; i++) {
                listElements[i].innerText = formStep4Inputs[i].value
            }
            listElements[listElements.length - 1].innerText = textArea.value

        }

        /**
         * Submit form
         *
         * validation, send data to server
         */

        submit(e) {
            let submitBoolean = true;

            // validation
            const quantity = document.querySelector("input[name='bags']")
            const organization = document.querySelector("input[name='organization']:checked")
            const listElements = form.querySelectorAll("div[data-step='5'] div.form-section--column li")
            const button = form.querySelector("div[data-step='5'] button[type='submit']")

            if (quantity.value < 1 || organization === null) {
                button.innerText = 'Uzupełnij dane'
                submitBoolean = false
                e.preventDefault();
            }
            for (let i = 0; i < listElements.length - 1; i++) {
                if (listElements[i].innerText === '') {
                    button.innerText = 'Uzupełnij dane'
                    submitBoolean = false;
                    e.preventDefault();
                }
            }

            if (submitBoolean) {
                this.currentStep++;
                this.updateForm();
            }
        }
    }

    const form = document.querySelector(".form--steps");
    if (form !== null) {
        new FormSteps(form);
    }
});

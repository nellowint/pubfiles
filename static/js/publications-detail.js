(function () {
    'use strict';

    function getCookie(name) {
        var value = '; ' + document.cookie;
        var parts = value.split('; ' + name + '=');
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    var ratingContainer = document.getElementById('ratingStars');
    if (ratingContainer) {
        var url = ratingContainer.getAttribute('data-url');
        var stars = ratingContainer.querySelectorAll('.star');
        var avgEl = document.getElementById('avgRating');

        stars.forEach(function (star) {
            star.addEventListener('click', function () {
                var score = star.getAttribute('data-score');
                var formData = new FormData();
                formData.append('score', score);

                fetch(url, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': getCookie('csrftoken') },
                    body: formData,
                })
                    .then(function (res) { return res.json(); })
                    .then(function (data) {
                        if (data.error) return;
                        stars.forEach(function (s) {
                            var sScore = parseInt(s.getAttribute('data-score'), 10);
                            if (sScore <= data.user_rating) {
                                s.classList.add('filled');
                            } else {
                                s.classList.remove('filled');
                            }
                        });
                        if (avgEl) avgEl.textContent = data.avg_rating;
                    })
                    .catch(function () {});
            });
        });
    }

    var editButtons = document.querySelectorAll('.js-edit-comment');
    editButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            var id = btn.getAttribute('data-id');
            var form = document.getElementById('comment-edit-form-' + id);
            var content = document.getElementById('comment-content-' + id);
            if (form && content) {
                form.style.display = 'block';
                content.style.display = 'none';
                btn.style.display = 'none';
            }
        });
    });

    var cancelButtons = document.querySelectorAll('.js-cancel-edit');
    cancelButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            var id = btn.getAttribute('data-id');
            var form = document.getElementById('comment-edit-form-' + id);
            var content = document.getElementById('comment-content-' + id);
            var editBtn = document.querySelector(
                '.js-edit-comment[data-id="' + id + '"]'
            );
            if (form && content) {
                form.style.display = 'none';
                content.style.display = 'block';
                if (editBtn) editBtn.style.display = '';
            }
        });
    });
})();

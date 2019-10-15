/**
 * Created by yifan_pan on 2019/10/15.
 */
export const fold = function(cardHeader) {
    if (!cardHeader) return;
    var cardBody = cardHeader.nextElementSibling;
    var triIcon = cardHeader.querySelector('.card-header-icon');
    if (triIcon) {
        triIcon.classList.toggle('icon-rotate');
    }
    cardBody.classList.toggle('card-body-collapsed');
    cardHeader.classList.toggle('card-header-active');
};

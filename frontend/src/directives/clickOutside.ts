/**
 * 点击外部指令 / Click Outside Directive
 *
 * 当点击元素外部时触发回调
 * Triggers callback when clicking outside element
 *
 * Author: AI Sprint
 * Date: 2026-04-07
 */

import type { DirectiveBinding, ObjectDirective } from 'vue'

interface ClickOutsideElement extends HTMLElement {
  _clickOutside?: (event: Event) => void
}

/**
 * 点击外部指令 / Click outside directive
 */
export const vClickOutside: ObjectDirective<ClickOutsideElement> = {
  mounted(el: ClickOutsideElement, binding: DirectiveBinding) {
    el._clickOutside = (event: Event) => {
      if (!(el === event.target || el.contains(event.target as Node))) {
        binding.value()
      }
    }
    document.addEventListener('click', el._clickOutside)
  },

  unmounted(el: ClickOutsideElement) {
    if (el._clickOutside) {
      document.removeEventListener('click', el._clickOutside)
    }
  }
}

export default vClickOutside

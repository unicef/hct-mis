import { AllAreasTreeQuery } from '../../../__generated__/graphql';

export class AreaTreeNode {
  id: string;

  checked: boolean | 'indeterminate';

  name: string;

  parent: AreaTreeNode;

  children: AreaTreeNode[];

  constructor(id, name) {
    this.id = id;
    this.name = name;
    this.children = [];
    this.checked = false; // false, true, 'indeterminate'
  }

  addChild(child): void {
    this.children.push(child);
    // eslint-disable-next-line no-param-reassign
    child.parent = this;
  }

  updateCheckStatus(): void {
    if (this.children.length === 0) return;

    const allChecked = this.children.every((child) => child.checked === true);
    const someChecked = this.children.some(
      (child) => child.checked === true || child.checked === 'indeterminate',
    );

    if (allChecked) {
      this.checked = true;
    } else if (someChecked) {
      this.checked = 'indeterminate';
    } else {
      this.checked = false;
    }

    if (this.parent) {
      this.parent.updateCheckStatus();
    }
  }

  updateCheckStatusFromTop(): void {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    let root: AreaTreeNode = this;
    while (root.parent) {
      root = root.parent;
    }

    const updateFromTop = (node: AreaTreeNode): void => {
      const allChecked = node.children.length
        ? node.children.every((child) => child.checked === true)
        : node.checked;
      const someChecked = node.children.some(
        (child) => child.checked === true || child.checked === 'indeterminate',
      );

      if (allChecked) {
        // eslint-disable-next-line no-param-reassign
        node.checked = true;
      } else if (someChecked && !allChecked) {
        // eslint-disable-next-line no-param-reassign
        node.checked = 'indeterminate';
      } else {
        // eslint-disable-next-line no-param-reassign
        node.checked = false;
      }

      node.children.forEach(updateFromTop);
    };

    updateFromTop(root);
  }

  updateCheckStatusFromRoot(): void {
    this.updateCheckStatus();
    if (this.parent) {
      this.parent.updateCheckStatusFromRoot();
    }
  }

  toggleCheck(): void {
    const newState = this.checked === false;
    this.setChecked(newState);
  }

  setChecked(newState): void {
    this.checked = newState;
    this.children.forEach((child) => child.setChecked(newState));
    this.updateCheckStatusFromRoot();
  }

  getSelectedIds(): string[] {
    const selectedIds: string[] = [];
    this.traverse((node) => {
      if (node.checked === true) {
        selectedIds.push(node.id);
      }
    });
    return selectedIds;
  }

  static getAllSelectedIds(nodes: AreaTreeNode[]): string[] {
    const selectedIds: string[] = [];
    nodes.forEach((node) => {
      selectedIds.push(...node.getSelectedIds());
    });
    return selectedIds;
  }

  // Private method to traverse the tree
  private traverse(callback: (node: AreaTreeNode) => void): void {
    callback(this);
    this.children.forEach((child) => child.traverse(callback));
  }

  static buildTree(
    areas: AllAreasTreeQuery['allAreasTree'],
    selectedIds: string[] = [],
  ): AreaTreeNode[] {
    const createNode = (
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      area: any,
      parent: AreaTreeNode | null,
    ): AreaTreeNode => {
      const node = new AreaTreeNode(area.id, area.name);
      if (selectedIds.includes(area.id)) {
        node.checked = true;
      }
      node.parent = parent;

      if (area.areas) {
        area.areas.forEach((childArea) => {
          const childNode = createNode(childArea, node);
          node.addChild(childNode);
        });
      }
      return node;
    };

    return areas.map((area) => {
      const node = createNode(area, null);
      node.updateCheckStatusFromTop();
      return node;
    });
  }
}
